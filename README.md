# SO Memory Kernel SDK

[![tests](https://github.com/Ika300/so-memory-kernel/actions/workflows/tests.yml/badge.svg)](https://github.com/Ika300/so-memory-kernel/actions/workflows/tests.yml)

A lightweight structural memory kernel for agents, workflows, RAG traces, and
relation data.

SO Memory Kernel is not an LLM, vector database, semantic search engine, or
summarizer. It does not try to guess what text "means" from natural language.
Instead, it accepts structured memory fragments and observes how their relations
repeat, connect, conflict, leave gaps, and become active again.

The core idea:

> Preserve memory as structure, not as approximate similarity.

SO Memory Kernel keeps separate signals that are often collapsed together:

- recurrence: which structures appear again?
- connection: which fragments bridge otherwise separate areas?
- tension: which relations conflict or pull against each other?
- gaps: where does structure imply a missing point?
- evidence identity: who supplied the evidence?
- pattern identity: which structural form is repeating?
- return / re-activation: when does a current structure touch a prior one again?

Japanese README: [README.ja.md](README.ja.md)

Release notes: [CHANGELOG.md](CHANGELOG.md)

## Why this exists

Most memory systems answer:

> What past text is similar to this input?

SO Memory Kernel asks a different question:

> Which structures are repeating, connecting, conflicting, leaving gaps, or
> becoming active again?

This makes it useful as a low-level memory layer underneath systems that already
produce structured traces:

- agent memory
- workflow memory
- RAG trace memory
- knowledge graph dynamics
- long-running reasoning systems
- structural analysis pipelines

It is deliberately small. The SDK does not replace your application, your LLM,
your database, or your retrieval layer. It provides a structural memory pass that
can sit beside them.

## Architecture at a glance

```text
MemoryFragment / MemoryRelation
        |
        v
SDK adapter
        |
        v
Copied Spiral Orbit Core
        |
        v
Structural memory signals
        |
        +-- Evidence Identity
        +-- Pattern Identity
        +-- Return / Re-activation
        +-- Insight JSON
```

The Kernel does not generate text. It returns structured signals that another
application, agent, or human can inspect.

## Who this is for

This project may be useful if you are building:

- an agent that needs traceable memory beyond chat history
- a RAG system that needs structural trace memory, not only document retrieval
- a workflow tool that needs to notice recurring blockers and re-activated tasks
- a knowledge system that wants exact structural recurrence without fuzzy merging
- an experimental cognitive or memory architecture

It is probably not the right tool if you need plug-and-play natural language
understanding, embeddings, vector search, or automatic summarization.

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

This boundary is intentional. The Kernel should not secretly introduce semantic
dictionaries, fuzzy merging, or hidden LLM interpretation into the memory core.

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
git clone https://github.com/Ika300/so-memory-kernel.git
cd so-memory-kernel
python examples/simple_memory_demo.py
```

Try the three most useful demos first:

```bash
python examples/evidence_identity_demo.py
python examples/reactivation_demo.py
python examples/rag_trace_memory_demo.py
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

The SDK exposes a small public API around the copied Spiral Orbit Core.

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
- [Comparison with vector search, RAG, knowledge graphs, and summarization](docs/comparison.md)
- [Services and consulting](docs/services.md)
- [Commercial path](docs/commercial_path.md)

Recommended first examples:

- `evidence_identity_demo.py`: shows the difference between one source repeated
  many times and many independent sources.
- `reactivation_demo.py`: shows strict structural re-activation without fuzzy
  semantic matching.
- `rag_trace_memory_demo.py`: shows how retrieval traces can preserve evidence
  identity and repeated structural exposure.

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

The most important benchmark claims are:

- repeated context is not confused with independent evidence
- exact Pattern Identity is preserved without semantic merging
- reversed direction does not collapse into the same structure
- unrelated noise does not create false Return candidates
- RAG traces can preserve source evidence and contextual recurrence separately

## Design constraints

The SDK must not:

- add arbitrary semantic dictionaries
- perform approximate semantic merging
- infer labels from natural language
- modify SO formulas, thresholds, Pattern types, or pipeline architecture
- mix LLM interpretation into the Core

These constraints are part of the product, not temporary limitations. SO Memory
Kernel is designed to preserve traceable structural difference instead of
flattening memory into one similarity score.

## Roadmap

- stabilize public API
- improve documentation
- add more examples
- prepare packaging
- keep Core behavior traceable and test-covered

## License

Apache-2.0
