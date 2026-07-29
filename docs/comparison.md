# Comparison with common memory approaches

SO Memory Kernel is not a replacement for existing memory infrastructure.

It is a structural memory pass that can sit beside vector search, RAG,
knowledge graphs, logs, and agent memory systems.

The shortest distinction is:

> Most memory systems retrieve similar content.
> SO Memory Kernel observes recurring structure.

## Summary table

| Approach | Main question | Typical output | What it may lose | SO Memory Kernel difference |
| --- | --- | --- | --- | --- |
| Vector search | What is similar? | nearest neighbors | direction, evidence identity, recurrence type | Tracks exact structural recurrence instead of similarity |
| RAG | What documents should be used for generation? | retrieved context | repeated exposure vs independent sources | Preserves source evidence and contextual recurrence separately |
| Knowledge graph | What entities and relations exist? | graph triples / paths | pattern repetition, gaps, re-activation | Observes how relation structures repeat, cluster, leave gaps, and return |
| Summarization | What is the shorter version? | compressed text | traceability and structural difference | Does not replace memory with paraphrase |
| Agent memory | What should the agent remember? | stored messages / facts | structural persistence across runs | Exposes evidence identity, pattern identity, and return candidates |

## Vector search

Vector search is useful when the system needs to find content that is close in
embedding space.

SO Memory Kernel asks a different question:

> Is this the same structural pattern appearing again?

For example, two memory fragments may use different words but should not be
merged unless the caller supplies a structure that makes them comparable. The
Kernel does not decide that "freedom" and "liberty" are the same. That is an
adapter or application decision.

This is intentional. The Kernel preserves structural difference unless structure
explicitly connects it.

Use vector search when you need:

- approximate semantic retrieval
- fuzzy matching
- large-scale document search

Use SO Memory Kernel when you need:

- exact structural recurrence
- direction preservation
- traceable evidence identity
- separation between repeated context and independent evidence

## RAG

RAG systems retrieve documents or chunks so a generator can answer a question.

SO Memory Kernel does not generate answers and does not choose final text for an
LLM. Instead, it can observe the structure of retrieval traces:

- which source documents repeatedly support the same relation
- whether many independent sources provide the same structure
- whether the same source is repeatedly exposed in many contexts
- whether a current retrieval pattern re-activates a prior one

This matters because "same evidence seen many times" and "many independent
pieces of evidence" are not the same thing.

SO Memory Kernel keeps those histories distinguishable.

## Knowledge graphs

Knowledge graphs store entities and relations.

SO Memory Kernel can consume relation-like data, but its purpose is different.
It does not only ask:

> What relation exists?

It also asks:

> How does this relation structure behave across overlays?

That means the Kernel can expose:

- repeated bridges
- directional chains
- tensions
- gaps
- clusters of confirmed structure
- return / re-activation candidates

A knowledge graph is often a memory surface. SO Memory Kernel is closer to a
structural dynamics pass over memory.

## Summarization

Summarization compresses content into shorter text.

SO Memory Kernel does not summarize. It preserves traceable structural outputs
that point back to source fragments.

This distinction is important:

- summarization replaces memory with a shorter representation
- SO Memory Kernel keeps source traceability and exposes structure derived from it

The Kernel should not make the source disappear.

## Agent memory

Many agent memory systems store:

- chat messages
- user facts
- task state
- tool logs
- retrieved documents

SO Memory Kernel can sit below or beside those systems as a structural memory
kernel.

It can help an agent distinguish:

- a recurring blocker from a one-time error
- one repeated source from many independent confirmations
- a current action that re-activates a prior failed pattern
- a bridge that keeps appearing across workflow traces

It does not decide what the agent should say. It exposes structural memory
signals that an agent, application, or human can use.

## What SO Memory Kernel intentionally does not do

SO Memory Kernel does not:

- infer natural-language meaning
- add semantic dictionaries
- create embeddings
- rank by semantic similarity
- generate answers
- rewrite user memory
- collapse distinct structures because they sound similar

These are not missing features in the core. They are boundaries.

Natural language parsing, embeddings, LLM interpretation, and domain-specific
meaning can be added by adapters or applications around the Kernel. The Kernel
itself should remain strict, traceable, and structurally conservative.

## When to use it

SO Memory Kernel is most useful when the input already has some structure:

- agent traces
- workflow events
- RAG retrieval traces
- relation records
- knowledge graph edges
- system logs converted into structural fragments
- human-curated memory fragments

It is least useful when the system expects it to read raw natural language and
infer meaning by itself.

## Core principle

SO Memory Kernel is built around one constraint:

> Do not flatten memory into one similarity score.

Memory can repeat.
Memory can conflict.
Memory can bridge.
Memory can leave gaps.
Memory can return.

Those are different structural events. The Kernel preserves them as different
signals.
