# SO Memory Kernel Benchmark Results

These benchmarks are deterministic structural checks. They are not LLM evaluations, semantic similarity tests, or natural-language understanding benchmarks.

## Summary

- Total: 7
- Passed: 7
- Failed: 0

## evidence_identity

Status: **PASS**

Expected:
- `condition_a_independent_source_count`: `1`
- `condition_a_contextual_recurrence_count`: `> 1`
- `condition_b_independent_source_count`: `3`

Observed:
- `condition_a_independent_source_count`: `1`
- `condition_a_contextual_recurrence_count`: `3`
- `condition_b_independent_source_count`: `3`
- `condition_b_contextual_recurrence_count`: `3`

## pattern_identity

Status: **PASS**

Expected:
- `bridge_group_count`: `1`
- `bridge_occurrence_count`: `3`
- `bridge_independent_source_count`: `3`

Observed:
- `bridge_group_count`: `1`
- `bridge_occurrence_count`: `3`
- `bridge_independent_source_count`: `3`

## direction_preservation

Status: **PASS**

Expected:
- `chain_identity_group_count`: `>= 2`
- `has_forward_chain`: `True`
- `has_reverse_chain`: `True`

Observed:
- `chain_identity_group_count`: `6`
- `has_forward_chain`: `True`
- `has_reverse_chain`: `True`

## return_reactivation

Status: **PASS**

Expected:
- `signal_return_candidate_count`: `>= 1`
- `control_return_candidate_count`: `0`

Observed:
- `signal_return_candidate_count`: `1`
- `control_return_candidate_count`: `0`
- `signal_current_fragment_ids`: `['current_design']`
- `signal_past_fragment_ids`: `['past_design']`

## no_semantic_guessing

Status: **PASS**

Expected:
- `return_candidate_count`: `0`
- `labels_remain_distinct`: `True`

Observed:
- `return_candidate_count`: `0`
- `pattern_identity_group_count`: `0`
- `labels_remain_distinct`: `True`

Notes:
- The Kernel does not merge freedom and liberty without caller-supplied structure.

## noise_robustness

Status: **PASS**

Expected:
- `signal_bridge_group_count`: `1`
- `return_candidate_count`: `>= 1`
- `false_return_candidates_from_noise`: `[]`

Observed:
- `noise_fragment_count`: `8`
- `signal_bridge_group_count`: `1`
- `return_candidate_count`: `1`
- `false_return_candidates_from_noise`: `[]`

## traceability

Status: **PASS**

Expected:
- `fragment_id_to_sentence_id_present`: `True`
- `sentence_id_to_fragment_id_present`: `True`
- `pattern_group_source_fragments_present`: `True`
- `return_current_fragments_present`: `True`
- `return_past_fragments_present`: `True`

Observed:
- `fragment_id_to_sentence_id_present`: `True`
- `sentence_id_to_fragment_id_present`: `True`
- `pattern_group_source_fragments_present`: `True`
- `return_current_fragments_present`: `True`
- `return_past_fragments_present`: `True`
