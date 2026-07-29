# Changelog

All notable changes to SO Memory Kernel will be documented in this file.

The format is intentionally simple. This project is still early, and public
releases should remain easy to audit.

## [0.1.0] - 2026-07-29

Initial public release.

### Added

- Public `so_memory` SDK wrapper.
- Copied Spiral Orbit Core under `spiral_orbit_core/`.
- `MemoryFragment`, `MemoryRelation`, and `MemoryKernel` public API.
- Adapter from SDK memory fragments into Spiral Orbit Core Structured JSON.
- Evidence Identity extraction:
  - independent source evidence
  - contextual recurrence evidence
- Pattern Identity grouping for exact structural recurrence.
- Return / Re-activation candidates based on exact Pattern Identity.
- Strict validation for caller-supplied memory fragments and relations.
- Examples:
  - simple memory demo
  - evidence identity demo
  - reactivation demo
  - agent memory demo
  - workflow memory demo
  - RAG trace memory demo
- Deterministic benchmark suite covering:
  - evidence identity
  - pattern identity
  - direction preservation
  - return / re-activation
  - no semantic guessing
  - noise robustness
  - traceability
  - agent memory traces
  - workflow blocker recurrence
  - RAG trace evidence
- Local RAG Trace Analyzer v0.1:
  - sanitized CSV input
  - local SO Memory Kernel execution
  - Markdown structural report
  - sample traces for repeated source, independent sources, and noisy retrieval
- English and Japanese README files.
- Public documentation for:
  - memory model
  - philosophy
  - comparison with common memory systems
  - use cases
  - benchmark snapshot
  - commercial path

### Design constraints

- The Kernel does not perform natural-language parsing.
- The Kernel does not add semantic dictionaries.
- The Kernel does not use embeddings.
- The Kernel does not perform approximate semantic merging.
- The Kernel does not generate answers.
- The Kernel preserves traceable structural signals instead of flattening memory
  into one similarity score.

### Verified

- Unit tests: 28 passing.
- Benchmarks: 10 passing, 0 failing.

### Notes

This release is an alpha SDK intended for experimentation with structural memory
in agents, workflows, RAG traces, relation data, and cognitive architecture
research.
