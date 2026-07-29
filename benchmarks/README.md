# Benchmarks

The benchmark suite is designed to verify the public claims of SO Memory
Kernel as a structural memory layer.

It answers questions such as:

- Can the Kernel distinguish one source repeated across many contexts from many
  independent sources?
- Can exact structural identity repeat without collapsing into semantic
  similarity?
- Can reversed direction remain distinct?
- Can current structure re-activate prior structure without fuzzy matching?
- Can unrelated noise be present without creating false structural returns?

Run:

```bash
python benchmarks/run_benchmarks.py
```

The runner writes:

- `benchmark_results/latest.json`
- `benchmark_results/latest.md`

These benchmarks are deterministic structural checks.

They do not evaluate LLM quality, semantic similarity, natural-language parsing,
or answer generation.

This is intentional. SO Memory Kernel should be tested as a structural memory
kernel, not as a language model.

## Cases

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

## Reading the results

The generated report is written to:

- `benchmark_results/latest.md`
- `benchmark_results/latest.json`

The tracked snapshot in `docs/benchmark_snapshot.md` records the latest checked
public benchmark state.

The most important failure modes to watch are:

- independent source evidence and contextual recurrence becoming indistinguishable
- Pattern Identity changing because repeated evidence was counted as a different
  structure
- direction being lost in Chain-like structures
- unrelated noise producing Return candidates
- traceability from SDK fragments back to SO source chains being broken
