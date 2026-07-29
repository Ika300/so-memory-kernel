from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "spiral_orbit_core"))

from spiral_orbit_microtopology import build_microtopologies
from spiral_orbit_models import SourceChain
from spiral_orbit_validation import SpiralOrbitValidationError, normalize_label


def structured_input(sentence_id: str = "s001") -> dict:
    return {
        "sentence_id": sentence_id,
        "raw_text": "Peace supports Growth.",
        "nodes": [
            {
                "label": " Peace ",
                "node_type": "value",
                "importance": 0.8,
                "persistence": 0.7,
                "valence": 0.6,
                "arousal": 0.3,
                "certainty": 0.9,
                "novelty": 0.4,
                "abstraction": 0.8,
            },
            {
                "label": "GROWTH",
                "node_type": "concept",
                "importance": 0.7,
                "persistence": 0.6,
                "valence": 0.5,
                "arousal": 0.4,
                "certainty": 0.8,
                "novelty": 0.5,
                "abstraction": 0.7,
            },
        ],
        "edges": [
            {
                "source": " Peace ",
                "target": "GROWTH",
                "relation_type": "support",
                "strength": 0.9,
                "directed": True,
            }
        ],
        "scores": {
            "importance": 0.8,
            "persistence": 0.7,
            "valence": 0.6,
            "arousal": 0.3,
            "certainty": 0.9,
            "novelty": 0.4,
            "bridge_potential": 0.2,
            "tension_score": 0.1,
            "gap_score": 0.1,
        },
        "categories": ["example"],
        "notes": [],
    }


class FoundationTests(unittest.TestCase):
    def test_normalize_label(self) -> None:
        self.assertEqual(normalize_label("  PEACE   now "), "peace now")

    def test_structured_json_creates_microtopology(self) -> None:
        result = build_microtopologies([structured_input()])
        self.assertEqual(len(result), 1)
        microtopology = result[0]
        self.assertEqual(microtopology.id, "mt_001")
        self.assertEqual(microtopology.nodes[0].id, "nd_001_001")
        self.assertEqual(microtopology.nodes[0].label, "peace")
        self.assertEqual(microtopology.edges[0].source, "peace")
        self.assertEqual(microtopology.edges[0].target, "growth")
        self.assertEqual(microtopology.source_chain.sentence_ids, ["s001"])
        self.assertEqual(microtopology.source_chain.microtopology_ids, ["mt_001"])

    def test_duplicate_sentence_id_is_rejected(self) -> None:
        with self.assertRaises(SpiralOrbitValidationError):
            build_microtopologies([structured_input(), structured_input()])

    def test_out_of_range_score_is_rejected_without_clamping(self) -> None:
        invalid = structured_input()
        invalid["scores"]["gap_score"] = 1.1
        with self.assertRaises(SpiralOrbitValidationError):
            build_microtopologies([invalid])

    def test_scores_must_be_float(self) -> None:
        invalid = structured_input()
        invalid["scores"]["importance"] = 1
        with self.assertRaises(SpiralOrbitValidationError):
            build_microtopologies([invalid])

    def test_source_chain_merge_preserves_first_seen_order(self) -> None:
        first = SourceChain(
            sentence_ids=["s001", "s002"],
            overlay_ids=["ov_001"],
            independent_source_sentence_ids=["s001"],
            independent_source_microtopology_ids=["mt_001"],
            contextual_recurrence_overlay_ids=["ov_001"],
        )
        second = SourceChain(
            sentence_ids=["s002", "s003"],
            overlay_ids=["ov_002"],
            independent_source_sentence_ids=["s002"],
            independent_source_microtopology_ids=["mt_002"],
            contextual_recurrence_overlay_ids=["ov_002"],
        )
        merged = SourceChain.merge(first, second)
        self.assertEqual(merged.sentence_ids, ["s001", "s002", "s003"])
        self.assertEqual(merged.overlay_ids, ["ov_001", "ov_002"])
        self.assertEqual(
            merged.independent_source_sentence_ids,
            ["s001", "s002"],
        )
        self.assertEqual(
            merged.independent_source_microtopology_ids,
            ["mt_001", "mt_002"],
        )
        self.assertEqual(
            merged.contextual_recurrence_overlay_ids,
            ["ov_001", "ov_002"],
        )


if __name__ == "__main__":
    unittest.main()
