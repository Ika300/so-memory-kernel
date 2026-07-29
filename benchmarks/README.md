# Benchmarks

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
