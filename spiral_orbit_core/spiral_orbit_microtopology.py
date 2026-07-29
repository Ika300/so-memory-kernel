from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from spiral_orbit_models import (
    EdgeFeature,
    GlobalScores,
    MicroTopology,
    NodeFeature,
    SourceChain,
)
from spiral_orbit_validation import (
    SpiralOrbitValidationError,
    normalize_label,
    validate_sentence_id,
)


def _require_fields(
    value: Mapping[str, Any], fields: Iterable[str], object_name: str
) -> None:
    missing = [field for field in fields if field not in value]
    if missing:
        raise SpiralOrbitValidationError(
            f"{object_name} is missing required fields: {', '.join(missing)}"
        )


def _build_node(
    node: Mapping[str, Any], microtopology_number: int, node_number: int
) -> NodeFeature:
    _require_fields(
        node,
        (
            "label",
            "node_type",
            "importance",
            "persistence",
            "valence",
            "arousal",
            "certainty",
            "novelty",
            "abstraction",
        ),
        "NodeFeature-compatible object",
    )
    return NodeFeature(
        id=f"nd_{microtopology_number:03d}_{node_number:03d}",
        label=normalize_label(node["label"]),
        node_type=node["node_type"],
        importance=node["importance"],
        persistence=node["persistence"],
        valence=node["valence"],
        arousal=node["arousal"],
        certainty=node["certainty"],
        novelty=node["novelty"],
        abstraction=node["abstraction"],
    )


def _build_edge(edge: Mapping[str, Any]) -> EdgeFeature:
    _require_fields(
        edge,
        ("source", "target", "relation_type", "strength", "directed"),
        "EdgeFeature-compatible object",
    )
    return EdgeFeature(
        source=normalize_label(edge["source"]),
        target=normalize_label(edge["target"]),
        relation_type=edge["relation_type"],
        strength=edge["strength"],
        directed=edge["directed"],
    )


def _build_scores(scores: Mapping[str, Any]) -> GlobalScores:
    _require_fields(
        scores,
        (
            "importance",
            "persistence",
            "valence",
            "arousal",
            "certainty",
            "novelty",
            "bridge_potential",
            "tension_score",
            "gap_score",
        ),
        "GlobalScores-compatible object",
    )
    return GlobalScores(**scores)


def build_microtopologies(
    structured_json_objects: list[Mapping[str, Any]],
) -> list[MicroTopology]:
    sentence_ids: set[str] = set()
    microtopologies: list[MicroTopology] = []

    for index, structured in enumerate(structured_json_objects, start=1):
        _require_fields(
            structured,
            (
                "sentence_id",
                "raw_text",
                "nodes",
                "edges",
                "scores",
                "categories",
                "notes",
            ),
            "Structured JSON object",
        )
        sentence_id = validate_sentence_id(structured["sentence_id"])
        if sentence_id in sentence_ids:
            raise SpiralOrbitValidationError(
                f"sentence_id must be unique per run: {sentence_id}"
            )
        sentence_ids.add(sentence_id)

        microtopology_id = f"mt_{index:03d}"
        nodes = [
            _build_node(node, index, node_index)
            for node_index, node in enumerate(structured["nodes"], start=1)
        ]
        edges = [_build_edge(edge) for edge in structured["edges"]]
        source_chain = SourceChain(
            sentence_ids=[sentence_id],
            microtopology_ids=[microtopology_id],
        )
        microtopologies.append(
            MicroTopology(
                id=microtopology_id,
                raw_text=structured["raw_text"],
                nodes=nodes,
                edges=edges,
                scores=_build_scores(structured["scores"]),
                categories=list(structured["categories"]),
                source_chain=source_chain,
                notes=list(structured["notes"]),
            )
        )

    return microtopologies
