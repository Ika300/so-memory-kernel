# SO Memory Kernel SDK

SO Memory Kernel is a lightweight structural memory SDK built around the copied
Spiral Orbit Core.

It is not an LLM, vector database, semantic search engine, or summarizer.

It is designed for structured memory fragments, event logs, agent traces,
workflow states, retrieval traces, and relation data.

It does not collapse memory into approximate similarity. Instead, it preserves
structural memory as:

- recurrence
- connection
- tension
- gaps
- evidence identity
- pattern identity
- return / re-activation

Japanese README: [README.ja.md](README.ja.md)

## Why this exists

Most memory systems answer:

> What past text is similar to this input?

SO Memory Kernel asks a different question:

> Which structures are repeating, connecting, conflicting, leaving gaps, or
> becoming active again?

This makes it useful as a low-level memory layer for:

- agent memory
- workflow memory
- RAG trace memory
- knowledge graph dynamics
- long-running reasoning systems
- structural analysis pipelines

## What it is not

SO Memory Kernel is not:

- a replacement for an LLM
- a vector database
- a RAG framework
- a text summarizer
- a natural language parser
- a semantic dictionary

Natural language parsing is an adapter problem. The Kernel accepts caller-supplied
structural fragments and relations.

## Current status

This repository currently contains:

- copied Spiral Orbit Core under `spiral_orbit_core/`
- public SDK wrapper under `so_memory/`
- examples under `examples/`
- tests under `tests/`

The original Spiral Orbit project is not modified.

## Quickstart

Clone the repository, then run:

```bash
python examples/simple_memory_demo.py
```

Run tests:

```bash
python -m unittest discover -s tests -p '*test*.py' -v
```

## Minimal usage

```python
from so_memory import MemoryFragment, MemoryKernel, MemoryRelation

kernel = MemoryKernel()

result = kernel.run([
    MemoryFragment(
        id="m1",
        content="A memory fragment connects memory and structure.",
        labels=["memory", "structure"],
        relations=[
            MemoryRelation(
                "memory",
                "structure",
                relation_type="bridge",
                strength=0.8,
                directed=False,
            )
        ],
        bridge_potential=0.8,
    )
])

print(result.has_insight)
print(result.evidence_identity.independent_source_count)
print(result.pattern_identity_groups)
print(result.return_candidates)
```

## Core concepts

### MemoryFragment

A minimal unit of structural memory. It keeps raw content as trace text and
accepts caller-supplied structural labels.

If labels are not supplied, the full fragment content is preserved as one
structural anchor. No dictionary is applied.

### MemoryRelation

A caller-supplied relation between labels.

Allowed relation types follow the copied SO Core:

- `support`
- `cause`
- `contrast`
- `tension`
- `bridge`
- `association`
- `dependency`

### Evidence Identity

Evidence Identity distinguishes:

- independent source evidence: who supplied the structure?
- contextual recurrence evidence: how often was the structure exposed across
  Overlay contexts?

It does not deduplicate Patterns or suppress repetition.

### Pattern Identity

Pattern Identity exposes exact structural recurrence.

A Pattern shares an identity only when these match exactly:

- Pattern type
- center candidate
- member node order
- edge relation and endpoint signature

This is not semantic similarity and not fuzzy merging.

### Return / Re-activation

Return is the moment when current structure re-touches a prior structural
identity.

Mark current fragments with:

```python
MemoryFragment(
    id="current_1",
    content="Current memory.",
    labels=["memory", "structure"],
    metadata={"phase": "current"},
)
```

Then inspect:

```python
for candidate in result.return_candidates:
    print(candidate.label, candidate.current_fragment_ids, candidate.past_fragment_ids)
```

v0.1 is intentionally strict: it only creates Return candidates when current and
past fragments share an exact Pattern Identity group in the same run.

## Examples

```bash
python examples/simple_memory_demo.py
python examples/evidence_identity_demo.py
python examples/reactivation_demo.py
python examples/agent_memory_demo.py
python examples/workflow_memory_demo.py
python examples/rag_trace_memory_demo.py
```

Use-case docs:

- [Agent / Workflow / RAG trace use cases](docs/use_cases.md)
- [Commercial path](docs/commercial_path.md)

## Benchmarks

Run:

```bash
python benchmarks/run_benchmarks.py
```

The benchmark suite writes:

- `benchmark_results/latest.json`
- `benchmark_results/latest.md`

Benchmark cases:

1. Evidence Identity
2. Pattern Identity
3. Direction Preservation
4. Return / Re-activation
5. No Semantic Guessing
6. Noise Robustness
7. Traceability
8. Agent Memory Trace
9. Workflow Blocker Recurrence
10. RAG Trace Evidence

These are deterministic structural checks, not LLM evaluations.

Latest checked snapshot: [docs/benchmark_snapshot.md](docs/benchmark_snapshot.md)

## Design constraints

The SDK must not:

- add arbitrary semantic dictionaries
- perform approximate semantic merging
- infer labels from natural language
- modify SO formulas, thresholds, Pattern types, or pipeline architecture
- mix LLM interpretation into the Core

## Roadmap

- stabilize public API
- improve documentation
- add more examples
- prepare packaging
- keep Core behavior traceable and test-covered

## License

Apache-2.0
