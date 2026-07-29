from __future__ import annotations

import argparse
import csv
import html
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from so_memory import MemoryFragment, MemoryKernel, MemoryKernelResult, MemoryRelation


REQUIRED_COLUMNS = {
    "trace_id",
    "query_id",
    "document_id",
    "chunk_id",
    "source_label",
    "relation_type",
    "target_label",
}


@dataclass(slots=True)
class RagTraceRecord:
    trace_id: str
    query_id: str
    document_id: str
    chunk_id: str
    source_label: str
    relation_type: str
    target_label: str
    strength: float = 0.7
    rank: str = ""
    score: str = ""
    phase: str = "past"


@dataclass(slots=True)
class RagTraceAnalysis:
    records: list[RagTraceRecord]
    result: MemoryKernelResult
    document_counts: Counter[str]
    query_counts: Counter[str]
    relation_counts: Counter[str]
    source_target_counts: Counter[tuple[str, str, str]]

    @property
    def total_records(self) -> int:
        return len(self.records)

    @property
    def unique_documents(self) -> int:
        return len(self.document_counts)

    @property
    def trace_origin_evidence_count(self) -> int:
        return self.total_records

    @property
    def top_document_share(self) -> float:
        if not self.records:
            return 0.0
        return self.document_counts.most_common(1)[0][1] / len(self.records)


def _clean_required(row: dict[str, str], name: str, line_number: int) -> str:
    value = (row.get(name) or "").strip()
    if not value:
        raise ValueError(f"missing required column value '{name}' at CSV line {line_number}")
    return value


def _parse_strength(row: dict[str, str], line_number: int) -> float:
    raw = (row.get("strength") or "").strip()
    if not raw:
        return 0.7
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"strength must be a float at CSV line {line_number}") from exc
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"strength must be from 0.0 to 1.0 at CSV line {line_number}")
    return value


def load_rag_trace_csv(path: Path) -> list[RagTraceRecord]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - fieldnames)
        if missing:
            raise ValueError(f"missing required CSV columns: {', '.join(missing)}")

        records: list[RagTraceRecord] = []
        seen_trace_ids: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            trace_id = _clean_required(row, "trace_id", line_number)
            if trace_id in seen_trace_ids:
                raise ValueError(f"trace_id must be unique: {trace_id}")
            seen_trace_ids.add(trace_id)

            records.append(
                RagTraceRecord(
                    trace_id=trace_id,
                    query_id=_clean_required(row, "query_id", line_number),
                    document_id=_clean_required(row, "document_id", line_number),
                    chunk_id=_clean_required(row, "chunk_id", line_number),
                    source_label=_clean_required(row, "source_label", line_number),
                    relation_type=_clean_required(row, "relation_type", line_number),
                    target_label=_clean_required(row, "target_label", line_number),
                    strength=_parse_strength(row, line_number),
                    rank=(row.get("rank") or "").strip(),
                    score=(row.get("score") or "").strip(),
                    phase=(row.get("phase") or "past").strip() or "past",
                )
            )
    if not records:
        raise ValueError("CSV contains no records")
    return records


def records_to_memory_fragments(records: Iterable[RagTraceRecord]) -> list[MemoryFragment]:
    fragments: list[MemoryFragment] = []
    for record in records:
        labels = [record.source_label, record.target_label, record.document_id]
        relation_type = record.relation_type
        fragments.append(
            MemoryFragment(
                id=record.trace_id,
                content=f"RAG trace {record.trace_id}: {record.source_label} {relation_type} {record.target_label}",
                labels=labels,
                relations=[
                    MemoryRelation(
                        source=record.source_label,
                        target=record.target_label,
                        relation_type=relation_type,
                        strength=record.strength,
                        directed=True,
                    ),
                    MemoryRelation(
                        source=record.document_id,
                        target=record.source_label,
                        relation_type="support",
                        strength=record.strength,
                        directed=True,
                    ),
                ],
                source_id=record.document_id,
                importance=record.strength,
                persistence=0.7,
                novelty=0.5,
                abstraction=0.6,
                bridge_potential=record.strength if relation_type == "bridge" else 0.0,
                tension_score=record.strength if relation_type == "tension" else 0.0,
                metadata={
                    "query_id": record.query_id,
                    "document_id": record.document_id,
                    "chunk_id": record.chunk_id,
                    "rank": record.rank,
                    "score": record.score,
                    "phase": record.phase,
                },
            )
        )
    return fragments


def analyze_records(records: list[RagTraceRecord]) -> RagTraceAnalysis:
    fragments = records_to_memory_fragments(records)
    result = MemoryKernel().run(fragments)
    return RagTraceAnalysis(
        records=records,
        result=result,
        document_counts=Counter(record.document_id for record in records),
        query_counts=Counter(record.query_id for record in records),
        relation_counts=Counter(record.relation_type for record in records),
        source_target_counts=Counter(
            (record.source_label, record.relation_type, record.target_label)
            for record in records
        ),
    )


def _format_counter(counter: Counter[str], limit: int = 10) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- `{key}`: {count}" for key, count in counter.most_common(limit)]


def _format_relation_counter(counter: Counter[tuple[str, str, str]], limit: int = 10) -> list[str]:
    if not counter:
        return ["- none"]
    lines = []
    for (source, relation_type, target), count in counter.most_common(limit):
        lines.append(f"- `{source}` --{relation_type}--> `{target}`: {count}")
    return lines


def _top_items(counter: Counter[str], limit: int = 10) -> list[tuple[str, int]]:
    return counter.most_common(limit)


def _top_relations(counter: Counter[tuple[str, str, str]], limit: int = 10) -> list[tuple[str, str, str, int]]:
    return [(source, relation_type, target, count) for (source, relation_type, target), count in counter.most_common(limit)]


def write_markdown_report(analysis: RagTraceAnalysis, output_path: Path) -> None:
    result = analysis.result

    lines: list[str] = [
        "# RAG Trace Structural Report",
        "",
        "Local structural analysis generated by SO Memory Kernel.",
        "",
        "No external AI API is used by this analyzer.",
        "",
        "## Input summary",
        "",
        f"- total trace records: {analysis.total_records}",
        f"- unique queries: {len(analysis.query_counts)}",
        f"- unique documents: {analysis.unique_documents}",
        f"- top document share: {analysis.top_document_share:.2f}",
        "",
        "## Evidence Identity",
        "",
        f"- trace-origin independent evidence: {analysis.trace_origin_evidence_count}",
        f"- document-level independent evidence: {analysis.unique_documents}",
        f"- SO contextual recurrence: {result.evidence_identity.contextual_recurrence_count}",
        "",
        "Interpretation guide:",
        "",
        "- trace-origin evidence counts distinct CSV trace records entering SO Memory Kernel.",
        "- document-level evidence counts distinct `document_id` values in the RAG trace CSV.",
        "- SO contextual recurrence counts repeated structural exposure observed after the Kernel run.",
        "- high SO contextual recurrence with low document-level evidence may mean the same document is being exposed repeatedly.",
        "- high document-level evidence means multiple retrieved documents are supporting structure.",
        "",
        "## Document concentration",
        "",
        *_format_counter(analysis.document_counts),
        "",
        "## Relation types",
        "",
        *_format_counter(analysis.relation_counts),
        "",
        "## Repeated source-relation-target structures",
        "",
        *_format_relation_counter(analysis.source_target_counts),
        "",
        "## Pattern Identity groups",
        "",
    ]

    if result.pattern_identity_groups:
        for group in sorted(
            result.pattern_identity_groups,
            key=lambda item: (item.occurrence_count, item.independent_source_count),
            reverse=True,
        )[:10]:
            lines.extend(
                [
                    f"- `{group.pattern_type}` / `{group.center_candidate}`",
                    f"  - occurrences: {group.occurrence_count}",
                    f"  - independent sources: {group.independent_source_count}",
                    f"  - contextual recurrence: {group.contextual_recurrence_count}",
                    f"  - member nodes: {', '.join(group.member_nodes)}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Return / Re-activation candidates", ""])
    if result.return_candidates:
        for candidate in result.return_candidates[:10]:
            lines.extend(
                [
                    f"- `{candidate.label}`",
                    f"  - return score: {candidate.return_score:.2f}",
                    f"  - current fragments: {', '.join(candidate.current_fragment_ids)}",
                    f"  - past fragments: {', '.join(candidate.past_fragment_ids)}",
                    f"  - caution: {candidate.caution}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This report is not an answer-quality score, not a faithfulness metric, and not an LLM evaluation.",
            "It is a local structural inspection of sanitized RAG trace records.",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _html_escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _metric_card(label: str, value: object, note: str = "") -> str:
    note_html = f"<p>{_html_escape(note)}</p>" if note else ""
    return (
        '<div class="metric-card">'
        f"<span>{_html_escape(label)}</span>"
        f"<strong>{_html_escape(value)}</strong>"
        f"{note_html}"
        "</div>"
    )


def _counter_table(title: str, rows: list[tuple[str, int]]) -> str:
    if not rows:
        body = '<tr><td colspan="2">none</td></tr>'
    else:
        body = "\n".join(
            f"<tr><td><code>{_html_escape(key)}</code></td><td>{count}</td></tr>"
            for key, count in rows
        )
    return (
        f"<section><h2>{_html_escape(title)}</h2>"
        '<table><thead><tr><th>Item</th><th>Count</th></tr></thead>'
        f"<tbody>{body}</tbody></table></section>"
    )


def _relation_table(rows: list[tuple[str, str, str, int]]) -> str:
    if not rows:
        body = '<tr><td colspan="4">none</td></tr>'
    else:
        body = "\n".join(
            "<tr>"
            f"<td><code>{_html_escape(source)}</code></td>"
            f"<td>{_html_escape(relation_type)}</td>"
            f"<td><code>{_html_escape(target)}</code></td>"
            f"<td>{count}</td>"
            "</tr>"
            for source, relation_type, target, count in rows
        )
    return (
        "<section><h2>Repeated source-relation-target structures</h2>"
        "<table><thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Count</th></tr></thead>"
        f"<tbody>{body}</tbody></table></section>"
    )


def write_html_report(analysis: RagTraceAnalysis, output_path: Path) -> None:
    result = analysis.result
    pattern_rows = []
    for group in sorted(
        result.pattern_identity_groups,
        key=lambda item: (item.occurrence_count, item.independent_source_count),
        reverse=True,
    )[:10]:
        pattern_rows.append(
            "<tr>"
            f"<td>{_html_escape(group.pattern_type)}</td>"
            f"<td><code>{_html_escape(group.center_candidate)}</code></td>"
            f"<td>{group.occurrence_count}</td>"
            f"<td>{group.independent_source_count}</td>"
            f"<td>{group.contextual_recurrence_count}</td>"
            f"<td>{_html_escape(', '.join(group.member_nodes))}</td>"
            "</tr>"
        )
    if not pattern_rows:
        pattern_rows.append('<tr><td colspan="6">none</td></tr>')

    return_rows = []
    for candidate in result.return_candidates[:10]:
        return_rows.append(
            "<tr>"
            f"<td><code>{_html_escape(candidate.label)}</code></td>"
            f"<td>{candidate.return_score:.2f}</td>"
            f"<td>{_html_escape(', '.join(candidate.current_fragment_ids))}</td>"
            f"<td>{_html_escape(', '.join(candidate.past_fragment_ids))}</td>"
            f"<td>{_html_escape(candidate.caution)}</td>"
            "</tr>"
        )
    if not return_rows:
        return_rows.append('<tr><td colspan="5">none</td></tr>')

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG Trace Structural Report</title>
  <style>
    :root {{
      --bg: #f6f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d9deea;
      --accent: #2f6feb;
      --soft: #eef4ff;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 56px; }}
    header {{
      background: linear-gradient(135deg, #18233f, #2f6feb);
      color: white;
      border-radius: 22px;
      padding: 34px;
      box-shadow: 0 18px 50px rgba(23, 32, 51, 0.18);
    }}
    header p {{ color: rgba(255,255,255,.82); max-width: 760px; }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 22px;
      margin-top: 20px;
      box-shadow: 0 10px 30px rgba(23, 32, 51, 0.06);
    }}
    h1, h2 {{ margin-top: 0; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 14px;
      margin-top: 20px;
    }}
    .metric-card {{
      background: var(--soft);
      border: 1px solid #d8e6ff;
      border-radius: 16px;
      padding: 16px;
    }}
    .metric-card span {{ display: block; color: var(--muted); font-size: 13px; }}
    .metric-card strong {{ display: block; font-size: 28px; margin-top: 4px; }}
    .metric-card p {{ margin: 6px 0 0; color: var(--muted); font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; overflow-wrap: anywhere; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 13px; }}
    code {{ background: #f1f3f8; border-radius: 6px; padding: 2px 5px; }}
    .note {{ color: var(--muted); }}
    .boundary {{ border-left: 5px solid var(--accent); }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>RAG Trace Structural Report</h1>
    <p>Local structural analysis generated by SO Memory Kernel. No external AI API is used by this analyzer.</p>
  </header>

  <section>
    <h2>Evidence at a glance</h2>
    <div class="metrics">
      {_metric_card("Trace records", analysis.total_records)}
      {_metric_card("Unique queries", len(analysis.query_counts))}
      {_metric_card("Unique documents", analysis.unique_documents)}
      {_metric_card("Top document share", f"{analysis.top_document_share:.2f}")}
      {_metric_card("Trace-origin evidence", analysis.trace_origin_evidence_count, "Distinct CSV trace records.")}
      {_metric_card("Document-level evidence", analysis.unique_documents, "Distinct document_id values.")}
      {_metric_card("SO contextual recurrence", result.evidence_identity.contextual_recurrence_count, "Repeated structural exposure after the Kernel run.")}
    </div>
  </section>

  <section class="boundary">
    <h2>Interpretation guide</h2>
    <p>High SO contextual recurrence with low document-level evidence may mean the same document is being exposed repeatedly.</p>
    <p>High document-level evidence means multiple retrieved documents are supporting structure.</p>
  </section>

  {_counter_table("Document concentration", _top_items(analysis.document_counts))}
  {_counter_table("Relation types", _top_items(analysis.relation_counts))}
  {_relation_table(_top_relations(analysis.source_target_counts))}

  <section>
    <h2>Pattern Identity groups</h2>
    <table>
      <thead><tr><th>Type</th><th>Center</th><th>Occurrences</th><th>Independent sources</th><th>Contextual recurrence</th><th>Member nodes</th></tr></thead>
      <tbody>{''.join(pattern_rows)}</tbody>
    </table>
  </section>

  <section>
    <h2>Return / Re-activation candidates</h2>
    <table>
      <thead><tr><th>Label</th><th>Score</th><th>Current fragments</th><th>Past fragments</th><th>Caution</th></tr></thead>
      <tbody>{''.join(return_rows)}</tbody>
    </table>
  </section>

  <section class="boundary">
    <h2>Boundary</h2>
    <p>This report is not an answer-quality score, not a faithfulness metric, and not an LLM evaluation.</p>
    <p>It is a local structural inspection of sanitized RAG trace records.</p>
  </section>
</main>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")


def analyze_csv(input_path: Path, output_path: Path, html_output_path: Path | None = None) -> RagTraceAnalysis:
    records = load_rag_trace_csv(input_path)
    analysis = analyze_records(records)
    write_markdown_report(analysis, output_path)
    if html_output_path is not None:
        write_html_report(analysis, html_output_path)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Local RAG Trace Analyzer for SO Memory Kernel")
    parser.add_argument("--input", required=True, help="Path to sanitized RAG trace CSV")
    parser.add_argument("--output", required=True, help="Path to Markdown report")
    parser.add_argument("--html-output", help="Optional path to basic static HTML report")
    args = parser.parse_args()

    analysis = analyze_csv(
        Path(args.input),
        Path(args.output),
        Path(args.html_output) if args.html_output else None,
    )
    print(f"RAG Trace Analyzer complete: {analysis.total_records} records")
    print(f"Report written to: {args.output}")
    if args.html_output:
        print(f"HTML report written to: {args.html_output}")


if __name__ == "__main__":
    main()
