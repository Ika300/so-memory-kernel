# Memory Model

SO Memory Kernel exposes a small public memory model.

## MemoryFragment

`MemoryFragment` is the smallest public input unit.

It contains:

- `id`
- `content`
- `labels`
- `relations`
- scores accepted by the copied SO Core
- `metadata`

The Kernel does not infer labels from `content`.

If labels are empty, the full content becomes one structural anchor.

## MemoryRelation

`MemoryRelation` is a caller-supplied edge between two labels.

Allowed relation types:

- `support`
- `cause`
- `contrast`
- `tension`
- `bridge`
- `association`
- `dependency`

## MemoryInput

`MemoryInput` is a list of fragments with unique ids.

## MemoryKernelResult

`MemoryKernelResult` contains:

- `insight`
- `structured_json`
- `fragment_id_to_sentence_id`
- `sentence_id_to_fragment_id`
- `evidence_identity`
- `pattern_identities`
- `pattern_identity_groups`
- `return_candidates`

## Evidence Identity

Evidence Identity is derived from SO SourceChain data.

It exposes:

- independent source sentence ids
- independent source fragment ids
- independent source microtopology ids
- contextual recurrence overlay ids

## Pattern Identity

Pattern Identity is an exact structural signature.

It is not semantic similarity.

## Return Candidate

Return Candidate is transient.

It appears when current fragments and prior fragments share an exact Pattern
Identity group.

No persistence or storage layer is involved in v0.1.
