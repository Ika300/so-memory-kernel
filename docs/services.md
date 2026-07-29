# Local toolkit and product direction

This page describes product direction, not an active paid service catalog.

The repository currently contains the free open-source SDK and basic local
tools. Paid packs may be developed separately later, but they are not included
in this repository unless explicitly stated.

## Current free scope

Included in this repository:

- SO Memory Kernel SDK
- basic Local RAG Trace Analyzer
- minimal sample traces
- Markdown report generation
- basic static HTML report generation
- examples
- tests
- benchmarks
- public docs

The free scope is meant to prove the behavior and make the project usable by
developers.

## Product direction

The safest product direction is local-first:

```text
User prepares sanitized structured records.
User runs the tool locally.
SO Memory Kernel produces structural signals.
No external AI API is used by default.
No customer data upload is required.
```

This avoids positioning the project as an AI service that receives private data.

## What the local toolkit does

- Reads sanitized CSV trace records.
- Runs SO Memory Kernel locally.
- Produces structural reports.
- Separates trace-origin recurrence from document-level recurrence.
- Shows document concentration.
- Shows repeated source-relation-target structures.
- Shows Pattern Identity groups.
- Shows Return / Re-activation candidates.

## What the local toolkit does not do

- It does not receive customer data.
- It does not send data to external AI APIs.
- It does not require raw documents.
- It does not perform natural-language understanding.
- It does not guarantee RAG answer quality.
- It does not replace evaluation frameworks.
- It does not require the maintainer to perform private technical diagnosis.

## Future paid packs

Future paid products may include:

- richer CSV templates
- more realistic sanitized sample traces
- report interpretation guide
- non-engineer local execution guide
- polished HTML report themes
- additional scenario packs

These should be sold separately from the free repository.

They should not require users to upload customer data.

## What should not be promised

Do not promise:

- private customer data analysis
- production integration support
- engineering diagnosis
- RAG quality guarantees
- LLM evaluation guarantees
- automatic document understanding

## Safe inquiry topics

Good public issue topics:

- local execution
- CSV schema
- sanitized sample shape
- report interpretation
- feature requests for the free local toolkit

Do not share private credentials, API keys, confidential customer data, or
proprietary raw logs/documents in a public GitHub issue.
