from __future__ import annotations

from collections import Counter
from collections.abc import Callable

from spiral_orbit_models import AttractorCluster, Pattern, SourceChain
from spiral_orbit_validation import (
    average,
    preserve_first_seen,
    status_for,
    transformative,
)


def _components(
    patterns: list[Pattern], connected: Callable[[Pattern, Pattern], bool]
) -> list[list[Pattern]]:
    remaining = list(patterns)
    result: list[list[Pattern]] = []
    while remaining:
        component = [remaining.pop(0)]
        changed = True
        while changed:
            changed = False
            for pattern in list(remaining):
                if any(connected(pattern, member) for member in component):
                    component.append(pattern)
                    remaining.remove(pattern)
                    changed = True
        result.append(component)
    return result


def _star_chain_groups(patterns: list[Pattern]) -> list[list[Pattern]]:
    eligible = [
        pattern for pattern in patterns if pattern.pattern_type in {"Star", "Chain"}
    ]
    return _components(
        eligible,
        lambda left, right: left.center_candidate == right.center_candidate,
    )


def _same_center_groups(
    patterns: list[Pattern], pattern_type: str
) -> list[list[Pattern]]:
    eligible = [
        pattern for pattern in patterns if pattern.pattern_type == pattern_type
    ]
    return _components(
        eligible,
        lambda left, right: left.center_candidate == right.center_candidate,
    )


def _gap_groups(patterns: list[Pattern]) -> list[list[Pattern]]:
    eligible = [pattern for pattern in patterns if pattern.pattern_type == "Gap"]
    return _components(
        eligible,
        lambda left, right: bool(set(left.member_nodes) & set(right.member_nodes))
        or bool(
            set(left.source_chain.sentence_ids) & set(right.source_chain.sentence_ids)
        ),
    )


def _gap_center(patterns: list[Pattern]) -> str:
    counts = Counter(node for pattern in patterns for node in pattern.member_nodes)
    highest_frequency = max(counts.values())
    candidates = [
        node for node, count in counts.items() if count == highest_frequency
    ]

    def importance(node: str) -> float:
        return average(
            pattern.node_importance_map[node]
            for pattern in patterns
            if node in pattern.node_importance_map
        )

    return sorted(candidates, key=lambda node: (-importance(node), node))[0]


def _cluster(
    patterns: list[Pattern],
    cluster_id: str,
    attractor_type: str,
) -> AttractorCluster:
    member_nodes = preserve_first_seen(
        node for pattern in patterns for node in pattern.member_nodes
    )
    member_edges = preserve_first_seen(
        edge for pattern in patterns for edge in pattern.member_edges
    )
    source_chain = SourceChain.merge(
        *(pattern.source_chain for pattern in patterns)
    ).with_id("cluster_ids", cluster_id)
    average_pattern_score = average(
        pattern.strength_score for pattern in patterns
    )
    pattern_count_factor = min(len(patterns) / 5, 1.0)
    recurrence_factor = min(len(set(source_chain.sentence_ids)) / 5, 1.0)
    member_factor = min(len(set(member_nodes)) / 3, 1.0)

    if attractor_type == "StarChain":
        cluster_score = (
            (0.40 * average_pattern_score)
            + (0.30 * pattern_count_factor)
            + (0.30 * recurrence_factor)
        )
        center = patterns[0].center_candidate
    elif attractor_type == "Tension":
        cluster_score = (0.60 * average_pattern_score) + (
            0.40 * pattern_count_factor
        )
        center = patterns[0].center_candidate
    elif attractor_type == "Bridge":
        bridge_factor = 1.0
        cluster_score = (0.80 * average_pattern_score) + (0.20 * bridge_factor)
        center = patterns[0].center_candidate
    else:
        cluster_score = (0.70 * average_pattern_score) + (0.30 * member_factor)
        center = _gap_center(patterns)

    novelty_score = average(pattern.novelty_score for pattern in patterns)
    average_importance = average(
        pattern.average_importance for pattern in patterns
    )
    average_abstraction = average(
        pattern.average_abstraction for pattern in patterns
    )
    transformative_score, is_transformative = transformative(
        novelty_score, average_importance, average_abstraction
    )
    return AttractorCluster(
        id=cluster_id,
        center=center,
        attractor_type=attractor_type,
        status=status_for(float(cluster_score)),
        cluster_score=float(cluster_score),
        supporting_pattern_ids=[pattern.id for pattern in patterns],
        supporting_pattern_types=preserve_first_seen(
            pattern.pattern_type for pattern in patterns
        ),
        member_nodes=member_nodes,
        member_edges=member_edges,
        novelty_score=float(novelty_score),
        average_importance=float(average_importance),
        average_abstraction=float(average_abstraction),
        recurrence_factor=float(recurrence_factor),
        pattern_count_factor=float(pattern_count_factor),
        member_factor=float(member_factor),
        source_chain=source_chain,
        transformative_score=transformative_score,
        is_transformative=is_transformative,
        notes=[],
    )


def _borderline_log(cluster: AttractorCluster) -> str:
    return (
        f"[AttractorCluster] id={cluster.id} type={cluster.attractor_type} "
        f"score={cluster.cluster_score} source_chain={cluster.source_chain}"
    )


def generate_attractor_clusters(
    patterns: list[Pattern], borderline_logs: list[str] | None = None
) -> list[AttractorCluster]:
    groups = [
        *(("StarChain", group) for group in _star_chain_groups(patterns)),
        *(("Tension", group) for group in _same_center_groups(patterns, "Tension")),
        *(("Bridge", group) for group in _same_center_groups(patterns, "Bridge")),
        *(("Gap", group) for group in _gap_groups(patterns)),
    ]
    confirmed: list[AttractorCluster] = []
    for index, (attractor_type, group) in enumerate(groups, start=1):
        cluster = _cluster(group, f"ac_{index:03d}", attractor_type)
        if cluster.status == "confirmed":
            confirmed.append(cluster)
        elif cluster.status == "borderline" and borderline_logs is not None:
            borderline_logs.append(_borderline_log(cluster))
    return confirmed
