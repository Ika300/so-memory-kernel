from __future__ import annotations

from itertools import combinations

from spiral_orbit_models import EdgeRecord, MicroTopology, OverlayResult, SourceChain
from spiral_orbit_validation import (
    average,
    maximum,
    preserve_first_seen,
    validate_unit_score,
)


def _real_edge_records(microtopology: MicroTopology) -> list[EdgeRecord]:
    return [
        EdgeRecord(
            source=edge.source,
            target=edge.target,
            relation_type=edge.relation_type,
            strength=edge.strength,
            directed=edge.directed,
            synthetic=False,
            source_microtopology_ids=[microtopology.id],
        )
        for edge in microtopology.edges
    ]


def _nodes_by_label(microtopology: MicroTopology) -> dict[str, list]:
    result: dict[str, list] = {}
    for node in microtopology.nodes:
        result.setdefault(node.label, []).append(node)
    return result


def _synthetic_tension_records(
    left: MicroTopology, right: MicroTopology, shared_nodes: list[str]
) -> list[EdgeRecord]:
    left_nodes = _nodes_by_label(left)
    right_nodes = _nodes_by_label(right)
    records: list[EdgeRecord] = []
    for label in shared_nodes:
        left_valences = [node.valence for node in left_nodes[label]]
        right_valences = [node.valence for node in right_nodes[label]]
        differences = [
            abs(left_valence - right_valence)
            for left_valence in left_valences
            for right_valence in right_valences
            if left_valence != 0.0
            and right_valence != 0.0
            and (left_valence > 0.0) != (right_valence > 0.0)
        ]
        if differences:
            strength = float(average(differences))
            validate_unit_score("synthetic tension strength", strength)
            records.append(
                EdgeRecord(
                    source=label,
                    target=label,
                    relation_type="tension",
                    strength=strength,
                    directed=False,
                    synthetic=True,
                    source_microtopology_ids=[left.id, right.id],
                )
            )
    return records


def _synthetic_bridge_records(
    microtopology: MicroTopology, real_records: list[EdgeRecord]
) -> list[EdgeRecord]:
    if microtopology.scores.bridge_potential < 0.70:
        return []
    if any(record.relation_type == "bridge" for record in real_records):
        return []
    if len(microtopology.nodes) < 2:
        return []
    ranked = sorted(
        enumerate(microtopology.nodes),
        key=lambda item: (-item[1].importance, item[0]),
    )
    first = ranked[0][1].label
    second = ranked[1][1].label
    return [
        EdgeRecord(
            source=first,
            target=second,
            relation_type="bridge",
            strength=microtopology.scores.bridge_potential,
            directed=False,
            synthetic=True,
            source_microtopology_ids=[microtopology.id],
        )
    ]


def _chain_paths(
    left_records: list[EdgeRecord], right_records: list[EdgeRecord]
) -> list[list[str]]:
    paths: list[list[str]] = []
    for first_records, second_records in (
        (left_records, right_records),
        (right_records, left_records),
    ):
        for first in first_records:
            for second in second_records:
                if first.target == second.source:
                    paths.append([first.source, first.target, second.target])
    return preserve_first_seen(paths)


def _gap_data(
    left: MicroTopology, right: MicroTopology
) -> tuple[list[str], dict[str, float]]:
    sources = [
        microtopology
        for microtopology in (left, right)
        if microtopology.scores.gap_score >= 0.70
    ]
    gap_nodes = preserve_first_seen(
        node.label for microtopology in sources for node in microtopology.nodes
    )
    importance: dict[str, float] = {}
    for label in gap_nodes:
        values = [
            node.importance
            for microtopology in sources
            for node in microtopology.nodes
            if node.label == label
        ]
        if values:
            importance[label] = float(average(values))
        else:
            importance[label] = float(
                average(
                    microtopology.scores.importance for microtopology in sources
                )
            )
    return gap_nodes, importance


def _build_overlay(
    left: MicroTopology, right: MicroTopology, overlay_number: int
) -> OverlayResult:
    overlay_id = f"ov_{overlay_number:03d}"
    left_real = _real_edge_records(left)
    right_real = _real_edge_records(right)
    real_records = [*left_real, *right_real]

    left_labels = {node.label for node in left.nodes}
    right_labels = {node.label for node in right.nodes}
    shared_nodes = sorted(left_labels & right_labels)
    shared_centers = sorted(
        {record.target for record in left_real}
        & {record.target for record in right_real}
    )
    shared_relation_types = sorted(
        {record.relation_type for record in left_real}
        & {record.relation_type for record in right_real}
    )

    synthetic_tensions = _synthetic_tension_records(left, right, shared_nodes)
    synthetic_bridges = [
        *_synthetic_bridge_records(left, left_real),
        *_synthetic_bridge_records(right, right_real),
    ]
    all_edge_records = [*real_records, *synthetic_tensions, *synthetic_bridges]
    tension_edges = [
        record for record in all_edge_records if record.relation_type == "tension"
    ]
    bridge_edges = [
        record for record in all_edge_records if record.relation_type == "bridge"
    ]
    bridge_pairs = preserve_first_seen(
        sorted([record.source, record.target]) for record in bridge_edges
    )
    chain_paths = _chain_paths(left_real, right_real)
    connected_chain_nodes = preserve_first_seen(path[1] for path in chain_paths)
    gap_nodes, gap_node_importance = _gap_data(left, right)

    support_strength = float(
        average(
            record.strength
            for record in all_edge_records
            if record.relation_type == "support"
        )
    )
    cause_strength = float(
        average(
            record.strength
            for record in all_edge_records
            if record.relation_type == "cause"
        )
    )
    contrast_strength = float(
        average(
            record.strength
            for record in all_edge_records
            if record.relation_type in {"contrast", "tension"}
        )
    )
    bridge_strength = float(
        maximum(
            [
                *(record.strength for record in bridge_edges),
                left.scores.bridge_potential,
                right.scores.bridge_potential,
            ]
        )
    )
    novelty_score = float(average([left.scores.novelty, right.scores.novelty]))
    average_gap_score = float(
        average([left.scores.gap_score, right.scores.gap_score])
    )
    average_importance = float(
        average([left.scores.importance, right.scores.importance])
    )
    average_abstraction = float(
        average(
            [node.abstraction for node in [*left.nodes, *right.nodes]],
            fallback=0.5,
        )
    )
    overlap_strength = float(
        (0.30 * (1.0 if shared_centers else 0.0))
        + (0.25 * (1.0 if shared_nodes else 0.0))
        + (0.20 * (1.0 if shared_relation_types else 0.0))
        + (0.15 * max(cause_strength, support_strength))
        + (0.10 * novelty_score)
    )
    validate_unit_score("overlap_strength", overlap_strength)

    source_chain = SourceChain.merge(left.source_chain, right.source_chain).with_id(
        "overlay_ids", overlay_id
    )
    return OverlayResult(
        id=overlay_id,
        source_microtopology_ids=[left.id, right.id],
        all_edge_records=all_edge_records,
        shared_centers=shared_centers,
        star_centers=list(shared_centers),
        shared_nodes=shared_nodes,
        shared_relation_types=shared_relation_types,
        connected_chain_nodes=connected_chain_nodes,
        chain_paths=chain_paths,
        tension_edges=tension_edges,
        bridge_edges=bridge_edges,
        bridge_pairs=bridge_pairs,
        gap_nodes=gap_nodes,
        gap_node_importance=gap_node_importance,
        novelty_score=novelty_score,
        support_strength=support_strength,
        cause_strength=cause_strength,
        contrast_strength=contrast_strength,
        bridge_strength=bridge_strength,
        average_gap_score=average_gap_score,
        average_importance=average_importance,
        average_abstraction=average_abstraction,
        overlap_strength=overlap_strength,
        source_chain=source_chain,
        notes=[],
    )


def generate_overlays(
    microtopologies: list[MicroTopology],
) -> list[OverlayResult]:
    return [
        _build_overlay(left, right, index)
        for index, (left, right) in enumerate(
            combinations(microtopologies, 2), start=1
        )
    ]
