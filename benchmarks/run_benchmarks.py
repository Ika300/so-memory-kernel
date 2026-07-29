from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark_cases import BENCHMARK_CASES, BenchmarkCaseResult
from so_memory import MemoryKernel


RESULTS_DIR = PROJECT_ROOT / "benchmark_results"


def _summary(results: list[BenchmarkCaseResult]) -> dict[str, int]:
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    return {"total": len(results), "passed": passed, "failed": failed}


def _json_payload(results: list[BenchmarkCaseResult]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": _summary(results),
        "cases": [asdict(result) for result in results],
    }


def _markdown(results: list[BenchmarkCaseResult]) -> str:
    summary = _summary(results)
    lines = [
        "# SO Memory Kernel Benchmark Results",
        "",
        "These benchmarks are deterministic structural checks. They are not LLM evaluations, semantic similarity tests, or natural-language understanding benchmarks.",
        "",
        "## Summary",
        "",
        f"- Total: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.name}",
                "",
                f"Status: **{result.status}**",
                "",
                "Expected:",
            ]
        )
        for key, value in result.expected.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.extend(["", "Observed:"])
        for key, value in result.observations.items():
            lines.append(f"- `{key}`: `{value}`")
        if result.notes:
            lines.extend(["", "Notes:"])
            for note in result.notes:
                lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines)


def run() -> dict[str, Any]:
    kernel = MemoryKernel()
    results = [case(kernel) for case in BENCHMARK_CASES]
    payload = _json_payload(results)
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (RESULTS_DIR / "latest.md").write_text(_markdown(results), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run()
    summary = payload["summary"]
    print(
        f"SO Memory Kernel benchmarks: {summary['passed']} passed, {summary['failed']} failed, {summary['total']} total"
    )
    raise SystemExit(0 if summary["failed"] == 0 else 1)
