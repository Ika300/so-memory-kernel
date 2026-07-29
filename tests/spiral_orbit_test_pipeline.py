from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "spiral_orbit_core"))

from spiral_orbit_pipeline import run_pipeline


def node(label: str, importance: float) -> dict:
    return {
        "label": label,
        "node_type": "concept",
        "importance": importance,
        "persistence": 0.9,
        "valence": 0.6,
        "arousal": 0.7,
        "certainty": 0.9,
        "novelty": 0.9,
        "abstraction": 0.8,
    }


def structured(sentence_id: str, labels: list[tuple[str, float]], bridge: float) -> dict:
    return {
        "sentence_id": sentence_id,
        "raw_text": sentence_id,
        "nodes": [node(label, importance) for label, importance in labels],
        "edges": [],
        "scores": {
            "importance": 0.9,
            "persistence": 0.9,
            "valence": 0.6,
            "arousal": 0.7,
            "certainty": 0.9,
            "novelty": 0.9,
            "bridge_potential": bridge,
            "tension_score": 0.2,
            "gap_score": 0.2,
        },
        "categories": [],
        "notes": [],
    }


class PipelineTests(unittest.TestCase):
    def test_bridge_path_reaches_insight_json(self) -> None:
        inputs = [
            structured("s001", [("alpha", 0.9), ("beta", 0.8)], 0.9),
            structured("s002", [("gamma", 0.7)], 0.0),
        ]
        insight = run_pipeline(inputs)
        self.assertIsNotNone(insight)
        assert insight is not None
        self.assertEqual(insight.id, "ij_001")
        self.assertEqual(insight.source_exploration_target_ids, ["et_001"])
        self.assertEqual(insight.questions[0].question_type, "NewConnection")
        self.assertEqual(insight.ideas[0].idea_type, "Bridge")
        self.assertEqual(
            insight.source_chain.insight_json_ids,
            ["ij_001"],
        )
        self.assertEqual(
            insight.source_chain.independent_source_sentence_ids,
            ["s001"],
        )
        self.assertEqual(
            insight.source_chain.independent_source_microtopology_ids,
            ["mt_001"],
        )
        self.assertEqual(
            insight.source_chain.contextual_recurrence_overlay_ids,
            ["ov_001"],
        )

    def test_no_confirmed_targets_returns_none(self) -> None:
        inputs = [
            structured("s001", [("alpha", 0.9)], 0.0),
            structured("s002", [("beta", 0.8)], 0.0),
        ]
        self.assertIsNone(run_pipeline(inputs))

    def test_pipeline_writes_only_borderline_log_file(self) -> None:
        inputs = [
            structured("s001", [("alpha", 0.9)], 0.0),
            structured("s002", [("beta", 0.8)], 0.0),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "logs").mkdir()
            run_pipeline(inputs, root)
            log_path = root / "logs" / "Spiral_Orbit_Borderline.log"
            self.assertTrue(log_path.exists())
            self.assertEqual(log_path.read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
