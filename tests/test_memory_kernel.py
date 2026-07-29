from __future__ import annotations

import unittest

from so_memory import MemoryFragment, MemoryKernel, MemoryKernelValidationError, MemoryRelation
from so_memory.adapter import memory_input_to_structured_json
from so_memory.models import MemoryInput


class MemoryKernelTests(unittest.TestCase):
    def test_fragment_validation_rejects_out_of_range_scores(self) -> None:
        with self.assertRaises(MemoryKernelValidationError):
            MemoryFragment(id="m1", content="alpha", importance=1.2)

    def test_adapter_preserves_caller_supplied_labels_without_dictionary(self) -> None:
        fragment = MemoryFragment(
            id="m1",
            content="A remembered structural fragment.",
            labels=["alpha", "beta"],
            relations=[MemoryRelation("alpha", "beta", relation_type="bridge", strength=0.8, directed=False)],
            bridge_potential=0.8,
        )
        structured, mapping = memory_input_to_structured_json(MemoryInput([fragment]))
        self.assertEqual(mapping, {"m1": "s001"})
        self.assertEqual(structured[0]["sentence_id"], "s001")
        self.assertEqual([node["label"] for node in structured[0]["nodes"]], ["alpha", "beta"])
        self.assertEqual(structured[0]["edges"][0]["relation_type"], "bridge")

    def test_fragment_without_labels_uses_content_as_single_anchor(self) -> None:
        fragment = MemoryFragment(id="m1", content="uninterpreted fragment")
        structured, _ = memory_input_to_structured_json(MemoryInput([fragment]))
        self.assertEqual(structured[0]["nodes"][0]["label"], "uninterpreted fragment")

    def test_kernel_runs_copied_so_core(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="m1",
                content="First memory links art and meaning.",
                labels=["art", "meaning"],
                relations=[MemoryRelation("art", "meaning", relation_type="bridge", strength=0.8, directed=False)],
                importance=0.8,
                novelty=0.7,
                bridge_potential=0.8,
            ),
            MemoryFragment(
                id="m2",
                content="Second memory repeats meaning and art in another context.",
                labels=["meaning", "art"],
                relations=[MemoryRelation("meaning", "art", relation_type="bridge", strength=0.75, directed=False)],
                importance=0.75,
                novelty=0.65,
                bridge_potential=0.75,
            ),
        ])
        self.assertTrue(result.has_insight)
        self.assertEqual(result.fragment_id_to_sentence_id["m1"], "s001")
        self.assertEqual(result.sentence_id_to_fragment_id["s002"], "m2")
        self.assertEqual(len(result.structured_json), 2)


if __name__ == "__main__":
    unittest.main()

class EvidenceIdentityTests(unittest.TestCase):
    def test_one_source_many_contexts_is_contextual_recurrence(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="bridge_source",
                content="One source supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.9, directed=False)],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(id="context_1", content="Unrelated context about weather.", labels=["weather"], importance=0.7, novelty=0.6),
            MemoryFragment(id="context_2", content="Unrelated context about food.", labels=["food"], importance=0.7, novelty=0.6),
            MemoryFragment(id="context_3", content="Unrelated context about traffic.", labels=["traffic"], importance=0.7, novelty=0.6),
        ])

        self.assertTrue(result.has_insight)
        self.assertEqual(result.evidence_identity.independent_source_fragment_ids, ["bridge_source"])
        self.assertEqual(result.evidence_identity.independent_source_count, 1)
        self.assertGreater(result.evidence_identity.contextual_recurrence_count, 1)

    def test_many_sources_same_bridge_are_independent_source_evidence(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="source_1",
                content="Source one supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.9, directed=False)],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(
                id="source_2",
                content="Source two independently supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.85, directed=False)],
                importance=0.85,
                novelty=0.75,
                bridge_potential=0.85,
            ),
            MemoryFragment(
                id="source_3",
                content="Source three independently supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.8, directed=False)],
                importance=0.8,
                novelty=0.7,
                bridge_potential=0.8,
            ),
        ])

        self.assertTrue(result.has_insight)
        self.assertEqual(
            result.evidence_identity.independent_source_fragment_ids,
            ["source_1", "source_2", "source_3"],
        )
        self.assertEqual(result.evidence_identity.independent_source_count, 3)
        self.assertGreaterEqual(result.evidence_identity.contextual_recurrence_count, 1)

class PatternIdentityTests(unittest.TestCase):
    def test_repeated_exact_bridge_patterns_share_identity_group(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="source_1",
                content="Bridge source one.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.9, directed=False)],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(
                id="source_2",
                content="Bridge source two.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.85, directed=False)],
                importance=0.85,
                novelty=0.75,
                bridge_potential=0.85,
            ),
            MemoryFragment(
                id="source_3",
                content="Bridge source three.",
                labels=["art", "religion"],
                relations=[MemoryRelation("art", "religion", relation_type="bridge", strength=0.8, directed=False)],
                importance=0.8,
                novelty=0.7,
                bridge_potential=0.8,
            ),
        ])

        bridge_groups = [
            group for group in result.pattern_identity_groups if group.pattern_type == "Bridge"
        ]
        self.assertEqual(len(bridge_groups), 1)
        self.assertEqual(bridge_groups[0].occurrence_count, 3)
        self.assertEqual(bridge_groups[0].independent_source_count, 3)
        self.assertEqual(bridge_groups[0].source_fragment_ids, ["source_1", "source_2", "source_3"])

    def test_duplicate_edge_evidence_does_not_split_pattern_identity(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="source_1",
                content="Bridge source one.",
                labels=["memory", "structure"],
                relations=[MemoryRelation("memory", "structure", relation_type="bridge", strength=0.9, directed=False)],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(
                id="source_2",
                content="Bridge source two.",
                labels=["memory", "structure"],
                relations=[MemoryRelation("memory", "structure", relation_type="bridge", strength=0.85, directed=False)],
                importance=0.85,
                novelty=0.75,
                bridge_potential=0.85,
            ),
        ])

        bridge_groups = [
            group
            for group in result.pattern_identity_groups
            if group.pattern_type == "Bridge" and set(group.member_nodes) == {"memory", "structure"}
        ]
        self.assertEqual(len(bridge_groups), 1)
        self.assertEqual(bridge_groups[0].source_fragment_ids, ["source_1", "source_2"])

    def test_directed_chain_patterns_with_reversed_direction_do_not_share_identity(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="forward_left",
                content="Forward chain left side.",
                labels=["a", "x", "c", "d"],
                relations=[
                    MemoryRelation("a", "x", relation_type="cause", strength=0.9, directed=True),
                    MemoryRelation("c", "d", relation_type="support", strength=0.9, directed=True),
                ],
                importance=0.9,
                novelty=0.8,
            ),
            MemoryFragment(
                id="forward_right",
                content="Forward chain right side.",
                labels=["x", "b", "e", "f"],
                relations=[
                    MemoryRelation("x", "b", relation_type="cause", strength=0.9, directed=True),
                    MemoryRelation("e", "f", relation_type="support", strength=0.9, directed=True),
                ],
                importance=0.9,
                novelty=0.8,
            ),
            MemoryFragment(
                id="reverse_left",
                content="Reverse chain left side.",
                labels=["b", "x", "g", "h"],
                relations=[
                    MemoryRelation("b", "x", relation_type="cause", strength=0.9, directed=True),
                    MemoryRelation("g", "h", relation_type="support", strength=0.9, directed=True),
                ],
                importance=0.9,
                novelty=0.8,
            ),
            MemoryFragment(
                id="reverse_right",
                content="Reverse chain right side.",
                labels=["x", "a", "i", "j"],
                relations=[
                    MemoryRelation("x", "a", relation_type="cause", strength=0.9, directed=True),
                    MemoryRelation("i", "j", relation_type="support", strength=0.9, directed=True),
                ],
                importance=0.9,
                novelty=0.8,
            ),
        ])

        chain_groups = [
            group for group in result.pattern_identity_groups if group.pattern_type == "Chain"
        ]
        chain_keys = {group.identity_key for group in chain_groups}
        self.assertGreaterEqual(len(chain_keys), 2)
        self.assertTrue(any("members=a,x,b" in key for key in chain_keys))
        self.assertTrue(any("members=b,x,a" in key for key in chain_keys))


class ReturnReactivationTests(unittest.TestCase):
    def test_current_fragment_reactivates_prior_exact_pattern_identity(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="past_1",
                content="Prior memory supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[
                    MemoryRelation(
                        "art",
                        "religion",
                        relation_type="bridge",
                        strength=0.9,
                        directed=False,
                    )
                ],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(
                id="current_1",
                content="Current memory supplies the same art religion bridge again.",
                labels=["art", "religion"],
                relations=[
                    MemoryRelation(
                        "art",
                        "religion",
                        relation_type="bridge",
                        strength=0.85,
                        directed=False,
                    )
                ],
                importance=0.85,
                novelty=0.75,
                bridge_potential=0.85,
                metadata={"phase": "current"},
            ),
        ])

        self.assertEqual(len(result.return_candidates), 1)
        candidate = result.return_candidates[0]
        self.assertEqual(candidate.current_fragment_ids, ["current_1"])
        self.assertEqual(candidate.past_fragment_ids, ["past_1"])
        self.assertEqual(candidate.shared_nodes, ["art", "religion"])
        self.assertGreater(candidate.return_score, 0.0)

    def test_no_current_marker_produces_no_return_candidates(self) -> None:
        kernel = MemoryKernel()
        result = kernel.run([
            MemoryFragment(
                id="source_1",
                content="Source one supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[
                    MemoryRelation(
                        "art",
                        "religion",
                        relation_type="bridge",
                        strength=0.9,
                        directed=False,
                    )
                ],
                importance=0.9,
                novelty=0.8,
                bridge_potential=0.9,
            ),
            MemoryFragment(
                id="source_2",
                content="Source two supplies the art religion bridge.",
                labels=["art", "religion"],
                relations=[
                    MemoryRelation(
                        "art",
                        "religion",
                        relation_type="bridge",
                        strength=0.85,
                        directed=False,
                    )
                ],
                importance=0.85,
                novelty=0.75,
                bridge_potential=0.85,
            ),
        ])

        self.assertEqual(result.return_candidates, [])

