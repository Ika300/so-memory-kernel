# SO Memory Kernel Philosophy

SO Memory Kernel treats memory as structure, not as approximate similarity.

A memory is not only something to retrieve. It may repeat, connect, conflict, leave gaps, or become active again under a new context.

The Kernel should preserve those movements without pretending to understand more than its inputs provide.

## Core principle

Do not crush distinct memories into one approximate meaning.

Preserve:

- independent source evidence
- contextual recurrence
- structural relations
- unresolved gaps
- reactivation paths

## Boundary

Natural language parsing is an adapter problem, not a Kernel responsibility.

## Evidence Identity

The problem is not repetition itself.

The problem is failing to distinguish same evidence seen many times from many independent evidences.

SO Memory Kernel preserves both:

- independent source evidence answers: who supplied the structure?
- contextual recurrence evidence answers: how often did the structure appear across contexts?

The Kernel should expose this distinction without reducing Pattern counts or flattening evidence into a single confidence score.

## Pattern Identity

Pattern Identity is not semantic similarity.

It is exact structural recurrence under the current Core output.

The Kernel should not collapse two Patterns merely because they look related. If direction, members, center, or edge signature differs, the identity should remain separate until a later reviewed design explicitly permits another relation.

## Return / Re-activation

Return is not search.

It is the moment when a current structure re-touches a prior structural identity.

In v0.1, Return remains deliberately strict: a candidate appears only when current
and past fragments share the same exact Pattern Identity group. This avoids
semantic guessing while making reactivation visible.

The Kernel should treat Return as a candidate, never as a conclusion.
