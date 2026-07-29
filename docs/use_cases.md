# Use cases

SO Memory Kernel is designed for structured memory fragments, event logs, agent
traces, workflow states, retrieval traces, and relation data.

It is not a natural-language reading tool.

## Agent Memory

Agent systems often store:

- observations
- tool calls
- failures
- retries
- blockers
- dependencies

SO Memory Kernel can represent these as `MemoryFragment` and `MemoryRelation`
objects, then expose:

- independent source evidence
- contextual recurrence
- exact Pattern Identity
- Return / re-activation candidates

Example:

```bash
python examples/agent_memory_demo.py
```

## Workflow Memory

Workflow and project systems often contain structured events:

- blocked tasks
- dependencies
- repeated failure modes
- module-to-module connections
- review states

SO Memory Kernel can track whether a blocker is merely repeated in context or
supported by independent workflow events.

Example:

```bash
python examples/workflow_memory_demo.py
```

## RAG Trace Memory

RAG systems already produce structured traces:

- retrieved chunk ids
- source ids
- supported claims
- relation labels
- confidence values

SO Memory Kernel can sit around those traces and expose whether evidence is
independent or repeated, and whether a current retrieval re-activates a prior
structure.

Example:

```bash
python examples/rag_trace_memory_demo.py
```

## Knowledge Graph Dynamics

Knowledge graphs often store static relations.

SO Memory Kernel is useful when the question is not only:

> What is connected to what?

but:

> Which structures are recurring, gaining evidence, or becoming active again?

## Boundary

Natural language parsing, extraction, and labeling should live in adapters above
the Kernel.

The Kernel itself should not invent labels, apply semantic dictionaries, or
merge approximate meanings.
