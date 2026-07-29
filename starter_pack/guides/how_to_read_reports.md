# How to Read RAG Trace Reports

The report is not asking whether the answer sounds good.
It asks what kind of evidence the RAG system actually used.

## 1. Independent evidence

Independent evidence means different source origins support the same answer.

A healthy report usually shows support from multiple document IDs, not only multiple chunks from one document.

## 2. Same-source recurrence

Same-source recurrence happens when the system repeatedly retrieves the same document or same source family.

This can make an answer feel well-supported even when the evidence base is narrow.

Useful question:

> Is this ten pieces of evidence, or one piece of evidence seen ten times?

## 3. Contextual recurrence

Contextual recurrence means the same structure appears across multiple retrieval situations.

This is not automatically bad. It may indicate that the same source is central. But it should not be mistaken for independent confirmation.

## 4. Noisy retrieval

Noise appears when high-ranking results are related by vocabulary but weakly related to the actual question.

Look for:

- high score but irrelevant text
- repeated generic wording
- policy-adjacent chunks that do not answer the query
- answer_used = true with weak support

## 5. Good client-facing language

Use cautious wording:

- "The answer appears to rely heavily on repeated evidence from one source."
- "The retrieval set contains supporting material, but independent confirmation is limited."
- "The system may be over-counting contextual recurrence as evidence breadth."

Avoid overclaiming:

- "The RAG system is broken."
- "The answer is hallucinated."
- "The documents prove the answer is wrong."

## 6. The main judgment

The best report separates three things:

1. What the system retrieved.
2. How independent that evidence was.
3. Whether the answer relied on narrow or broad support.
