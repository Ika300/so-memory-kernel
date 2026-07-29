# RAG Trace Analyzer sample reports

These reports are public demo outputs generated from sanitized sample CSV files.

They are included so readers can understand the analyzer without running the
tool first.

No raw documents, private data, external AI API calls, or customer traces are
used.

## Main demo question

```text
Does the RAG trace show many independent documents,
or the same document appearing repeatedly?
```

This is the core distinction Local RAG Trace Analyzer is designed to make easier
to inspect.

## Compare these two reports first

| Case | Trace records | Unique documents | Top document share | Suggested reading |
| --- | ---: | ---: | ---: | --- |
| [Repeated same source](repeated_same_source_report.md) | 4 | 1 | 1.00 | Several trace records exist, but they all come from one document. This may indicate repeated exposure rather than independent document support. |
| [Independent sources](independent_sources_report.md) | 4 | 4 | 0.25 | Several trace records exist and they come from several documents. This is closer to independent document support. |

## HTML previews

The same reports are also available as basic static HTML:

- [Repeated same source HTML](repeated_same_source_report.html)
- [Independent sources HTML](independent_sources_report.html)

The HTML output is intentionally basic and free. Polished report themes may be
developed separately later.

## What to notice

### Repeated same source

Important lines:

```text
unique documents: 1
top document share: 1.00
document-level independent evidence: 1
```

Interpretation:

The trace has multiple records, but the evidence is concentrated in one
document. A RAG system may appear to have repeated support while actually seeing
the same document repeatedly.

### Independent sources

Important lines:

```text
unique documents: 4
top document share: 0.25
document-level independent evidence: 4
```

Interpretation:

The trace has multiple records and multiple documents. This is structurally
different from repeated exposure to one document.

## Boundary

These reports do not claim:

- answer quality
- factual correctness
- faithfulness
- RAG accuracy
- LLM evaluation

They only show local structural inspection of sanitized RAG trace records.
