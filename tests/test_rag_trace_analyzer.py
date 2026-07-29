from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.rag_trace_analyzer.rag_trace_analyzer import (
    analyze_csv,
    load_rag_trace_csv,
    records_to_memory_fragments,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "tools" / "rag_trace_analyzer" / "sample_traces"


class RagTraceAnalyzerTests(unittest.TestCase):
    def test_load_sample_trace(self) -> None:
        records = load_rag_trace_csv(SAMPLES / "repeated_same_source.csv")
        self.assertEqual(len(records), 4)
        self.assertEqual(records[0].document_id, "doc_policy_a")

    def test_records_convert_to_memory_fragments_without_raw_documents(self) -> None:
        records = load_rag_trace_csv(SAMPLES / "independent_sources.csv")
        fragments = records_to_memory_fragments(records)
        self.assertEqual(len(fragments), 4)
        self.assertIn("retrieval", fragments[0].labels)
        self.assertIn("answer_basis", fragments[0].labels)
        self.assertIn("doc_policy_a", fragments[0].labels)

    def test_analyzer_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.md"
            analysis = analyze_csv(SAMPLES / "independent_sources.csv", output)
            report = output.read_text(encoding="utf-8")
        self.assertEqual(analysis.total_records, 4)
        self.assertIn("# RAG Trace Structural Report", report)
        self.assertIn("No external AI API is used", report)
        self.assertIn("trace-origin independent evidence", report)
        self.assertIn("document-level independent evidence", report)

    def test_analyzer_writes_basic_html_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_output = Path(tmpdir) / "report.md"
            html_output = Path(tmpdir) / "report.html"
            analyze_csv(SAMPLES / "repeated_same_source.csv", markdown_output, html_output)
            report = html_output.read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", report)
        self.assertIn("RAG Trace Structural Report", report)
        self.assertIn("No external AI API is used", report)
        self.assertIn("Document-level evidence", report)

    def test_missing_required_column_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "bad.csv"
            csv_path.write_text("trace_id,query_id\nx,q\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_rag_trace_csv(csv_path)


if __name__ == "__main__":
    unittest.main()
