# Commercial path

SO Memory Kernel should be positioned as a developer-facing structural memory
Kernel, not a natural-language report generator.

## Open source layer

Public:

- SO Memory Kernel SDK
- examples
- benchmarks
- documentation

Purpose:

- trust
- technical proof
- developer adoption
- integration examples

## Paid layers

Possible paid offerings should live above the Kernel.

### Agent Memory Audit

Review an AI agent or LLM application's memory design and describe how it could
represent memory as fragments, relations, evidence identity, Pattern Identity,
and Return candidates.

### Integration Pack

Build a small adapter for a customer's structured data:

- agent traces
- workflow events
- RAG retrieval traces
- task dependency logs
- knowledge graph deltas

Deliverables may include:

- `MemoryFragment` design
- `MemoryRelation` design
- adapter sample
- benchmark result
- integration notes

### Paid Adapters

Adapters may be commercial while the Kernel remains open:

- agent trace adapter
- RAG trace adapter
- workflow event adapter
- task graph adapter
- knowledge graph delta adapter

## What not to sell first

Avoid positioning the first product as:

- natural-language understanding
- automatic text reading
- summarization
- generic document analysis

Those are adapter/product-layer problems, not Kernel responsibilities.

## Core message

SO Memory Kernel adds structural memory to systems that already have structured
events, relations, or traces.
