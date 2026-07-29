# Local toolkit and product direction

SO Memory Kernel is open source.

The commercial direction is not to receive customer data and analyze it with AI.
The safer direction is:

> Help users inspect their own structured memory traces locally.

This means:

- no customer data upload by default
- no external AI API by default
- no raw document submission required
- no LLM analysis service
- local structural processing with SO Memory Kernel

## Product direction

The first commercial product should be a local toolkit, not a consulting-heavy
service.

Recommended product:

```text
Local RAG Trace Analyzer Kit
```

The kit helps users inspect sanitized RAG retrieval traces on their own machine.

## What the toolkit does

- Reads sanitized CSV trace records.
- Runs SO Memory Kernel locally.
- Produces Markdown or HTML-style structural reports.
- Separates trace-origin recurrence from document-level recurrence.
- Shows document concentration.
- Shows repeated source-relation-target structures.
- Shows Pattern Identity groups.
- Shows Return / Re-activation candidates.

## What the toolkit does not do

- It does not receive customer data.
- It does not send data to external AI APIs.
- It does not require raw documents.
- It does not perform natural-language understanding.
- It does not guarantee RAG answer quality.
- It does not replace evaluation frameworks.
- It does not require the maintainer to perform private technical diagnosis.

## Why this is safer

Some users may dislike or prohibit sending data to AI systems.

SO Memory Kernel can avoid that problem because it is not an LLM. A local toolkit
can run on sanitized structured records such as:

```csv
trace_id,query_id,document_id,chunk_id,source_label,relation_type,target_label,strength
t001,q001,doc_a,c001,retrieval,bridge,answer_basis,0.82
```

The user can prepare or redact this data before running the tool.

## Free layer

The public repository can include:

- SDK
- basic RAG Trace Analyzer CLI
- sample CSV files
- sample Markdown report
- benchmark cases
- public documentation

Purpose:

- trust
- proof of behavior
- developer adoption
- public evidence that the Kernel is local and structural

## Starter Pack layer

A future paid Starter Pack could include:

- richer CSV templates
- more realistic sanitized RAG trace examples
- report interpretation guide
- checklist for repeated evidence vs independent evidence
- common trace-shape recipes
- no-data-upload operating guide
- local execution walkthrough

The Starter Pack should not require receiving customer data.

## Optional setup boundary

If setup help is offered later, it should be limited to:

- installing the local toolkit
- running sample data
- explaining the input CSV format
- explaining how to read the generated report

It should not promise:

- private data analysis
- engineering diagnosis
- RAG quality guarantees
- integration ownership
- production support

## Best first market

The best first users are:

- individual RAG developers
- small AI builders
- AI contractors who want local trace inspection
- internal AI teams that cannot upload data to external AI services

## Core sales message

```text
Your RAG may not have more evidence.
It may be seeing the same evidence repeatedly.
```

SO Memory Kernel helps inspect that difference locally.

## Safe inquiry format

Users should not send private data in public issues.

Useful public questions are about:

- CSV schema
- sanitized sample shape
- local execution
- report interpretation
- feature requests for the local toolkit

Do not share private credentials, API keys, confidential customer data, or
proprietary raw logs/documents in a public GitHub issue.
