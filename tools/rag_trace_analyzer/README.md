# Local RAG Trace Analyzer v0.1

Local RAG Trace Analyzer is a small CLI tool built on SO Memory Kernel.

It reads sanitized structured RAG retrieval traces from CSV and produces a
Markdown structural report.

It does not use external AI APIs.
It does not require raw documents.
It does not send customer data anywhere.
It does not evaluate answer quality.

Its first purpose is narrow:

> Distinguish repeated exposure from independent source evidence in RAG traces.

See also: [`docs/rag_trace_analyzer.md`](../../docs/rag_trace_analyzer.md)

## Input CSV

Required columns:

- `trace_id`
- `query_id`
- `document_id`
- `chunk_id`
- `source_label`
- `relation_type`
- `target_label`

Optional columns:

- `strength`
- `rank`
- `score`
- `phase`

Allowed `relation_type` values follow SO Memory Kernel:

- `support`
- `cause`
- `contrast`
- `tension`
- `bridge`
- `association`
- `dependency`

## Run

From the repository root:

```bash
python tools/rag_trace_analyzer/rag_trace_analyzer.py \
  --input tools/rag_trace_analyzer/sample_traces/repeated_same_source.csv \
  --output tools/rag_trace_analyzer/report.md
```

On Windows PowerShell:

```powershell
py -3 tools\rag_trace_analyzer\rag_trace_analyzer.py --input tools\rag_trace_analyzer\sample_traces\repeated_same_source.csv --output tools\rag_trace_analyzer\report.md
```

## Sample traces

- `repeated_same_source.csv`: one document appears repeatedly across contexts.
- `independent_sources.csv`: multiple documents provide the same structure.
- `noisy_retrieval.csv`: signal records mixed with unrelated retrieval noise.

## Report sections

- Input summary
- Evidence Identity
- Document concentration
- Relation types
- Repeated source-relation-target structures
- Pattern Identity groups
- Return / Re-activation candidates

## Boundary

This tool is not:

- a RAG accuracy score
- a faithfulness metric
- a summarizer
- an LLM evaluator
- a natural-language parser

It is a local structural inspection tool for sanitized RAG trace records.
