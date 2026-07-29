from __future__ import annotations

import argparse
import csv
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


def write_markdown_report(analysis: RagTraceAnalysis, output_path: Path) -> None:
    result = analysis.result
    evidence = result.evidence_identity

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
        f"- trace-origin independent evidence: {evidence.independent_source_count}",
        f"- document-level independent evidence: {analysis.unique_documents}",
        f"- contextual recurrence: {evidence.contextual_recurrence_count}",
        "",
        "Interpretation guide:",
        "",
        "- trace-origin evidence counts distinct trace records entering SO Memory Kernel.",
        "- document-level evidence counts distinct `document_id` values in the RAG trace CSV.",
        "- high contextual recurrence with low document-level evidence may mean the same document is being exposed repeatedly.",
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


def analyze_csv(input_path: Path, output_path: Path) -> RagTraceAnalysis:
    records = load_rag_trace_csv(input_path)
    analysis = analyze_records(records)
    write_markdown_report(analysis, output_path)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Local RAG Trace Analyzer for SO Memory Kernel")
    parser.add_argument("--input", required=True, help="Path to sanitized RAG trace CSV")
    parser.add_argument("--output", required=True, help="Path to Markdown report")
    args = parser.parse_args()

    analysis = analyze_csv(Path(args.input), Path(args.output))
    print(f"RAG Trace Analyzer complete: {analysis.total_records} records")
    print(f"Report written to: {args.output}")


if __name__ == "__main__":
    main()
