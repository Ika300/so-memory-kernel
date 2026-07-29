# Commercial path

This repository is the free open-source layer.

It contains:

- SO Memory Kernel SDK
- basic Local RAG Trace Analyzer
- examples
- benchmarks
- tests
- minimal sample CSV files
- public documentation

It does not contain paid packs or private customer work.

## Boundary

The commercial direction should remain local-first and data-safe.

```text
GitHub repository = free OSS SDK + basic local tools
Paid products later = separate template/report packs
Customer data upload = not required
External AI API = not used by default
```

This distinction matters because users may not want customer data, internal RAG
traces, or proprietary logs sent to AI systems.

SO Memory Kernel can be useful without receiving user data. The user can run the
tool locally on sanitized structured records.

## Free layer

The free layer should be enough to prove the technical behavior.

Included:

- installable Python SDK
- small public examples
- deterministic benchmarks
- basic RAG Trace Analyzer CLI
- three minimal sample traces
- Markdown report generation
- basic static HTML report generation
- public docs explaining the boundaries

Purpose:

- trust
- technical proof
- reproducibility
- GitHub adoption
- public demonstration of local structural processing

## Future paid layer

Future paid products should be separate from this repository unless explicitly
released as free.

Possible paid products:

- Starter Template Pack
- Report Template Pack
- Industry Trace Template Pack
- Non-engineer Local Execution Guide
- Polished HTML Report Themes
- Additional sanitized scenario packs

These paid products should not require the maintainer to receive customer data.

## What should stay free

Keep these free:

- SDK core API
- basic CLI analyzer
- minimal sample traces
- basic report output
- tests
- benchmarks
- core documentation

The free layer must remain useful enough to build trust.

## What may become paid later

Possible paid additions:

- richer RAG trace schemas
- more realistic sanitized examples
- report interpretation guide
- polished report templates
- non-engineer walkthroughs
- checklist for repeated exposure vs independent evidence
- packaging for easy local use

These should be framed as convenience, education, and packaging, not hidden core
functionality.

## What not to sell

Avoid selling:

- private data analysis
- customer data upload
- external-AI analysis of customer files
- engineering diagnosis
- production integration ownership
- RAG accuracy guarantees
- LLM evaluation guarantees
- automatic natural-language understanding

Those promises create too much risk and do not match the safest product shape.

## First commercial hypothesis

The first realistic paid product is:

```text
Local RAG Trace Analyzer Starter Pack
```

It would build on the free analyzer and add better templates, examples, and
reading guides.

Core message:

```text
Your RAG may not have more evidence.
It may be seeing the same evidence repeatedly.
```

The user runs the analysis locally. No customer data upload is required.
