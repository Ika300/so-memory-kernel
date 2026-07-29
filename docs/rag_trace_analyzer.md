# Local RAG Trace Analyzer

Local RAG Trace Analyzer is the first product-shaped tool built on SO Memory
Kernel.

It is designed for one practical question:

> Is a RAG system seeing many independent pieces of evidence, or repeatedly
> seeing the same evidence?

The tool reads sanitized structured CSV traces and runs locally. It does not use
external AI APIs and does not require raw documents.

## Why this matters

RAG evaluation often focuses on answer quality, faithfulness, or retrieval score.
Those are important, but they do not always show whether the retrieval history
has independent support.

Two situations can look similar:

```text
Case A: one document appears repeatedly
Case B: many documents support the same structure
```

Both may look like repeated support. Structurally, they are different.

SO Memory Kernel helps keep that difference visible.

## What the analyzer reads

The analyzer expects sanitized CSV records.

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

Example:

```csv
trace_id,query_id,document_id,chunk_id,source_label,relation_type,target_label,strength
t001,q001,doc_policy_a,c001,retrieval,bridge,answer_basis,0.82
```

The input should not contain private raw documents, credentials, API keys, or
confidential customer content.

## What the report shows

The Markdown report includes:

- total trace records
- unique queries
- unique documents
- top document share
- trace-origin independent evidence
- document-level independent evidence
- SO contextual recurrence
- document concentration
- repeated source-relation-target structures
- Pattern Identity groups
- Return / Re-activation candidates

## Demo cases

### Case A: repeated same source

Input:

- 4 trace records
- 4 queries
- 1 document
- repeated `retrieval --bridge--> answer_basis`

Expected reading:

- trace-origin evidence is high because several trace records exist
- document-level evidence is low because all records use one document
- top document share is 1.00
- this may indicate repeated exposure, not independent document support

Sample output:

- [`repeated_same_source_report.md`](../tools/rag_trace_analyzer/sample_reports/repeated_same_source_report.md)
- [`repeated_same_source_report.html`](../tools/rag_trace_analyzer/sample_reports/repeated_same_source_report.html)

### Case B: independent sources

Input:

- 4 trace records
- 3 queries
- 4 documents
- repeated `retrieval --bridge--> answer_basis`

Expected reading:

- trace-origin evidence is high
- document-level evidence is also high
- top document share is low
- this is closer to independent document support

Sample output:

- [`independent_sources_report.md`](../tools/rag_trace_analyzer/sample_reports/independent_sources_report.md)
- [`independent_sources_report.html`](../tools/rag_trace_analyzer/sample_reports/independent_sources_report.html)

### Case C: noisy retrieval

Input:

- signal traces mixed with unrelated retrieval records
- policy documents plus weather, lunch, sports, and travel records

Expected reading:

- noise remains visible as unrelated relation structures
- signal structures can still appear as repeated Pattern Identity groups
- this is not an answer quality judgment

## Run locally

From the repository root:

```bash
python tools/rag_trace_analyzer/rag_trace_analyzer.py \
  --input tools/rag_trace_analyzer/sample_traces/repeated_same_source.csv \
  --output tools/rag_trace_analyzer/report.md \
  --html-output tools/rag_trace_analyzer/report.html
```

On Windows PowerShell:

```powershell
py -3 tools\rag_trace_analyzer\rag_trace_analyzer.py --input tools\rag_trace_analyzer\sample_traces\repeated_same_source.csv --output tools\rag_trace_analyzer\report.md --html-output tools\rag_trace_analyzer\report.html
```

## Boundary

Local RAG Trace Analyzer is not:

- a RAG accuracy score
- a faithfulness metric
- an LLM evaluator
- a natural-language parser
- a document analysis service
- a production monitoring system

It is a local structural inspection tool for sanitized RAG trace records.

## Free vs future paid boundary

This repository includes the free basic analyzer.

Free scope:

- basic CLI
- minimal sample traces
- Markdown report output
- basic static HTML report output
- public documentation

Future paid packs may be developed separately later:

- richer CSV templates
- polished report templates
- additional sanitized scenario packs
- non-engineer reading guides

Those future packs are not included in this repository unless explicitly stated.

The safe commercial direction is not to ask users to upload data. The stronger
direction is:

```text
Run this locally on sanitized traces.
Inspect whether retrieval support is independent or merely repeated.
```

No customer data upload is required for this product direction.
