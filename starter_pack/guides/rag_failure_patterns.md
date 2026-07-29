# RAG Failure Patterns

Use these patterns when interpreting analyzer output.

## 1. Same-source illusion

The retrieval result looks broad because many chunks are returned, but most come from the same document.

Risk:
The answer may appear better supported than it really is.

## 2. High-score noise

A result has a high retrieval score but does not actually answer the question.

Risk:
The answer may be pulled toward vocabulary similarity instead of evidence relevance.

## 3. Context collapse

Several different questions retrieve the same small group of chunks.

Risk:
The system may overuse a narrow evidence neighborhood.

## 4. Missing independent confirmation

The answer has one plausible source but no second independent source.

Risk:
The answer may be fragile when source wording is incomplete or ambiguous.

## 5. Repeated near-duplicates

Many chunks say almost the same thing.

Risk:
The answer may over-count repetition as confirmation.

## 6. Unused strong evidence

Relevant retrieved chunks exist but are not used in the final answer.

Risk:
The generation step may be ignoring useful retrieval.
