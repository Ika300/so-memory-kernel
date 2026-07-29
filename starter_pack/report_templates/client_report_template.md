# Client Report Template

# RAG Evidence Trace Review

## 1. Executive finding

The retrieval trace suggests that the system may be relying on:

- [ ] broad independent evidence
- [ ] repeated evidence from a narrow source set
- [ ] noisy or weakly relevant retrieval
- [ ] mixed evidence that requires manual review

Short conclusion:

> Write the main finding here in one or two sentences.

## 2. Evidence independence

Observed source breadth:

- Number of trace rows reviewed:
- Number of unique documents:
- Number of repeated-source clusters:

Interpretation:

> Explain whether the answer appears supported by independent sources or repeated exposure to the same source.

## 3. Recurrence pattern

Observed recurrence:

> Describe whether the same documents, chunks, or evidence structures appear repeatedly.

Why it matters:

> Repetition may be useful, but it should not be mistaken for independent confirmation.

## 4. Retrieval noise

Potential noise observed:

- [ ] high-score but weakly relevant chunks
- [ ] adjacent-topic chunks
- [ ] duplicated or near-duplicated chunks
- [ ] answer-used chunks with unclear support

Interpretation:

> Explain the practical risk in cautious language.

## 5. Recommended review focus

The next manual review should focus on:

1. Whether the answer depends on one dominant source.
2. Whether independent supporting documents exist.
3. Whether high-ranked chunks actually answer the query.
4. Whether repeated chunks are being over-counted as evidence.

## 6. Caution

This report analyzes retrieval evidence structure. It does not prove legal, factual, or compliance correctness by itself.
