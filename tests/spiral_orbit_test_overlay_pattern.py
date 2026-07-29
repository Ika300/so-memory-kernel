from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "spiral_orbit_core"))

from spiral_orbit_microtopology import build_microtopologies
from spiral_orbit_overlay import generate_overlays
from spiral_orbit_pattern import generate_patterns


def node(label: str, importance: float = 0.8, valence: float = 0.4) -> dict:
    return {
        "label": label,
        "node_type": "concept",
        "importance": importance,
        "persistence": 0.8,
        "valence": valence,
        "arousal": 0.6,
        "certainty": 0.9,
        "novelty": 0.8,
        "abstraction": 0.7,
    }


def source(
    sentence_id: str,
    nodes: list[dict],
    edges: list[dict],
    *,
    bridge_potential: float = 0.0,
    gap_score: float = 0.0,
) -> dict:
    return {
        "sentence_id": sentence_id,
        "raw_text": sentence_id,
        "nodes": nodes,
        "edges": edges,
        "scores": {
            "importance": 0.9,
            "persistence": 0.8,
            "valence": 0.4,
            "arousal": 0.6,
            "certainty": 0.9,
            "novelty": 0.8,
            "bridge_potential": bridge_potential,
            "tension_score": 0.8,
            "gap_score": gap_score,
        },
        "categories": [],
        "notes": [],
    }


def edge(source_label: str, target_label: str, relation: str, strength=0.9) -> dict:
    return {
        "source": source_label,
        "target": target_label,
        "relation_type": relation,
        "strength": float(strength),
        "directed": True,
    }


class OverlayPatternTests(unittest.TestCase):
    def test_overlay_pair_count_and_source_chain(self) -> None:
        inputs = [
            source("s001", [node("a")], []),
            source("s002", [node("b")], []),
            source("s003", [node("c")], []),
        ]
        overlays = generate_overlays(build_microtopologies(inputs))
        self.assertEqual(len(overlays), 3)
        self.assertEqual(overlays[0].source_chain.overlay_ids, ["ov_001"])

    def test_chain_path_and_confirmed_chain_pattern(self) -> None:
        inputs = [
            source(
                "s001",
                [node("a"), node("x"), node("c"), node("d")],
                [edge("a", "x", "cause"), edge("c", "d", "support")],
            ),
            source(
                "s002",
                [node("x"), node("b"), node("e"), node("f")],
                [edge("x", "b", "cause"), edge("e", "f", "support")],
            ),
        ]
        overlay = generate_overlays(build_microtopologies(inputs))[0]
        self.assertEqual(overlay.chain_paths, [["a", "x", "b"]])
        patterns = generate_patterns([overlay])
        chain = next(pattern for pattern in patterns if pattern.pattern_type == "Chain")
        self.assertEqual(chain.member_nodes, ["a", "x", "b"])
        self.assertEqual(len(chain.member_edges), 2)

    def test_synthetic_bridge_and_bridge_pattern(self) -> None:
        inputs = [
            source(
                "s001",
                [node("alpha", 0.9), node("beta", 0.8)],
                [],
                bridge_potential=0.9,
            ),
            source("s002", [node("gamma")], []),
        ]
        overlay = generate_overlays(build_microtopologies(inputs))[0]
        self.assertEqual(overlay.bridge_pairs, [["alpha", "beta"]])
        self.assertTrue(overlay.bridge_edges[0].synthetic)
        bridge = next(
            pattern
            for pattern in generate_patterns([overlay])
            if pattern.pattern_type == "Bridge"
        )
        self.assertEqual(bridge.source_nodes, ["alpha"])
        self.assertEqual(bridge.target_nodes, ["beta"])
        self.assertEqual(bridge.member_nodes, ["alpha", "beta"])
        self.assertEqual(
            bridge.source_chain.independent_source_sentence_ids,
            ["s001"],
        )
        self.assertEqual(
            bridge.source_chain.independent_source_microtopology_ids,
            ["mt_001"],
        )
        self.assertEqual(
            bridge.source_chain.contextual_recurrence_overlay_ids,
            ["ov_001"],
        )

    def test_bridge_evidence_distinguishes_two_independent_sources(self) -> None:
        inputs = [
            source(
                "s001",
                [node("art"), node("religion")],
                [edge("art", "religion", "bridge")],
            ),
            source(
                "s002",
                [node("art"), node("religion")],
                [edge("art", "religion", "bridge")],
            ),
        ]
        overlay = generate_overlays(build_microtopologies(inputs))[0]
        bridge = next(
            pattern
            for pattern in generate_patterns([overlay])
            if pattern.pattern_type == "Bridge"
        )
        self.assertEqual(
            bridge.source_chain.independent_source_sentence_ids,
            ["s001", "s002"],
        )
        self.assertEqual(
            bridge.source_chain.independent_source_microtopology_ids,
            ["mt_001", "mt_002"],
        )
        self.assertEqual(
            bridge.source_chain.contextual_recurrence_overlay_ids,
            ["ov_001"],
        )

    def test_gap_pattern_retains_importance_map(self) -> None:
        inputs = [
            source(
                "s001",
                [node("high", 0.9), node("low", 0.4)],
                [],
                gap_score=0.9,
            ),
            source("s002", [node("other")], [], gap_score=0.8),
        ]
        overlay = generate_overlays(build_microtopologies(inputs))[0]
        gap = next(
            pattern
            for pattern in generate_patterns([overlay])
            if pattern.pattern_type == "Gap"
        )
        self.assertEqual(gap.center_candidate, "high")
        self.assertEqual(gap.node_importance_map["high"], 0.9)

    def test_synthetic_tension_from_valence_conflict(self) -> None:
        inputs = [
            source("s001", [node("shared", valence=0.5)], []),
            source("s002", [node("shared", valence=-0.5)], []),
        ]
        overlay = generate_overlays(build_microtopologies(inputs))[0]
        self.assertEqual(len(overlay.tension_edges), 1)
        self.assertTrue(overlay.tension_edges[0].synthetic)
        tension = next(
            pattern
            for pattern in generate_patterns([overlay])
            if pattern.pattern_type == "Tension"
        )
        self.assertEqual(tension.member_nodes, ["shared"])


if __name__ == "__main__":
    unittest.main()
