from __future__ import annotations

from collections.abc import Callable

from spiral_orbit_models import EdgeRecord, OverlayResult, Pattern
from spiral_orbit_validation import (
    preserve_first_seen,
    status_for,
    transformative,
)


def _pattern(
    overlay: OverlayResult,
    pattern_id: str,
    pattern_type: str,
    strength_score: float,
    center_candidate: str,
    source_nodes: list[str],
    target_nodes: list[str],
    member_nodes: list[str],
    member_edges: list[EdgeRecord],
    node_importance_map: dict[str, float] | None = None,
) -> Pattern:
    transformative_score, is_transformative = transformative(
        overlay.novelty_score,
        overlay.average_importance,
        overlay.average_abstraction,
    )
    independent_source_microtopology_ids = preserve_first_seen(
        microtopology_id
        for edge in member_edges
        for microtopology_id in edge.source_microtopology_ids
    )
    sentence_id_by_microtopology_id = dict(
        zip(
            overlay.source_microtopology_ids,
            overlay.source_chain.sentence_ids,
            strict=True,
        )
    )
    independent_source_sentence_ids = preserve_first_seen(
        sentence_id_by_microtopology_id[microtopology_id]
        for microtopology_id in independent_source_microtopology_ids
    )
    source_chain = (
        overlay.source_chain.with_id("pattern_ids", pattern_id).with_evidence_history(
            independent_source_sentence_ids=independent_source_sentence_ids,
            independent_source_microtopology_ids=independent_source_microtopology_ids,
            contextual_recurrence_overlay_ids=[overlay.id],
        )
    )
    return Pattern(
        id=pattern_id,
        pattern_type=pattern_type,
        status=status_for(strength_score),
        strength_score=float(strength_score),
        center_candidate=center_candidate,
        source_nodes=source_nodes,
        target_nodes=target_nodes,
        member_nodes=member_nodes,
        member_edges=member_edges,
        node_importance_map=node_importance_map or {},
        source_overlay_ids=[overlay.id],
        novelty_score=overlay.novelty_score,
        average_importance=overlay.average_importance,
        average_abstraction=overlay.average_abstraction,
        source_chain=source_chain,
        transformative_score=transformative_score,
        is_transformative=is_transformative,
        notes=[],
    )


def _connected_sources(
    records: list[EdgeRecord], target_nodes: list[str]
) -> list[str]:
    return preserve_first_seen(
        record.source for record in records if record.target in target_nodes
    )


def _matching_chain_edges(
    records: list[EdgeRecord], path: list[str]
) -> list[EdgeRecord]:
    first = next(
        (
            record
            for record in records
            if record.source == path[0] and record.target == path[1]
        ),
        None,
    )
    second = next(
        (
            record
            for record in records
            if record.source == path[1] and record.target == path[2]
        ),
        None,
    )
    if first is None or second is None:
        return []
    return [first, second]


def _generate_candidates(
    overlay: OverlayResult, next_id: Callable[[], str]
) -> list[Pattern]:
    candidates: list[Pattern] = []

    if overlay.star_centers:
        target_nodes = list(overlay.star_centers)
        source_nodes = _connected_sources(overlay.all_edge_records, target_nodes)
        member_edges = [
            record
            for record in overlay.all_edge_records
            if record.target in overlay.star_centers
        ]
        member_nodes = preserve_first_seen([*target_nodes, *source_nodes])
        candidates.append(
            _pattern(
                overlay,
                next_id(),
                "Star",
                (0.70 * overlay.overlap_strength)
                + (0.30 * overlay.support_strength),
                sorted(overlay.star_centers)[0],
                source_nodes,
                target_nodes,
                member_nodes,
                member_edges,
            )
        )

    for path in overlay.chain_paths:
        member_edges = _matching_chain_edges(overlay.all_edge_records, path)
        if len(member_edges) != 2:
            continue
        candidates.append(
            _pattern(
                overlay,
                next_id(),
                "Chain",
                (0.50 * overlay.cause_strength)
                + (0.30 * overlay.support_strength)
                + (0.20 * overlay.overlap_strength),
                path[2],
                [path[0]],
                [path[2]],
                list(path),
                member_edges,
            )
        )

    if overlay.tension_edges:
        source_nodes = preserve_first_seen(
            record.source for record in overlay.tension_edges
        )
        target_nodes = preserve_first_seen(
            record.target for record in overlay.tension_edges
        )
        candidates.append(
            _pattern(
                overlay,
                next_id(),
                "Tension",
                (0.70 * overlay.contrast_strength)
                + (0.30 * overlay.overlap_strength),
                sorted(source_nodes)[0],
                source_nodes,
                target_nodes,
                preserve_first_seen([*source_nodes, *target_nodes]),
                list(overlay.tension_edges),
            )
        )

    for pair in overlay.bridge_pairs:
        member_edges = [
            record
            for record in overlay.bridge_edges
            if sorted([record.source, record.target]) == pair
        ]
        candidates.append(
            _pattern(
                overlay,
                next_id(),
                "Bridge",
                (0.80 * overlay.bridge_strength)
                + (0.20 * overlay.novelty_score),
                f"{pair[0]}<->{pair[1]}",
                [pair[0]],
                [pair[1]],
                [pair[0], pair[1]],
                member_edges,
            )
        )

    if overlay.gap_nodes:
        center = sorted(
            overlay.gap_nodes,
            key=lambda node: (-overlay.gap_node_importance[node], node),
        )[0]
        candidates.append(
            _pattern(
                overlay,
                next_id(),
                "Gap",
                (0.70 * overlay.average_gap_score)
                + (0.30 * overlay.average_importance),
                center,
                [],
                list(overlay.gap_nodes),
                list(overlay.gap_nodes),
                [],
                dict(overlay.gap_node_importance),
            )
        )

    return candidates


def _borderline_log(pattern: Pattern) -> str:
    return (
        f"[Pattern] id={pattern.id} type={pattern.pattern_type} "
        f"score={pattern.strength_score} source_chain={pattern.source_chain}"
    )


def generate_patterns(
    overlays: list[OverlayResult], borderline_logs: list[str] | None = None
) -> list[Pattern]:
    sequence = 0

    def next_id() -> str:
        nonlocal sequence
        sequence += 1
        return f"pt_{sequence:03d}"

    confirmed: list[Pattern] = []
    for overlay in overlays:
        for pattern in _generate_candidates(overlay, next_id):
            if pattern.status == "confirmed":
                confirmed.append(pattern)
            elif pattern.status == "borderline" and borderline_logs is not None:
                borderline_logs.append(_borderline_log(pattern))
    return confirmed
