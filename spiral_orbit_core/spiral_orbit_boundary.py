from __future__ import annotations

from spiral_orbit_models import AttractorCluster, Boundary
from spiral_orbit_validation import status_for, transformative


BOUNDARY_MAPPING = {
    "Gap": "GapBoundary",
    "Tension": "TensionBoundary",
    "Bridge": "BridgeBoundary",
    "StarChain": "ExpansionBoundary",
}


def _score(cluster: AttractorCluster) -> float:
    if cluster.attractor_type in {"Gap", "Tension"}:
        return cluster.cluster_score
    if cluster.attractor_type == "Bridge":
        return (0.70 * cluster.cluster_score) + (0.30 * 1.0)
    return (0.60 * cluster.cluster_score) + (0.40 * cluster.recurrence_factor)


def _borderline_log(boundary: Boundary) -> str:
    return (
        f"[Boundary] id={boundary.id} type={boundary.boundary_type} "
        f"score={boundary.boundary_score} source_chain={boundary.source_chain}"
    )


def generate_boundaries(
    clusters: list[AttractorCluster], borderline_logs: list[str] | None = None
) -> list[Boundary]:
    confirmed: list[Boundary] = []
    for index, cluster in enumerate(clusters, start=1):
        boundary_id = f"bd_{index:03d}"
        boundary_score = float(_score(cluster))
        transformative_score, is_transformative = transformative(
            cluster.novelty_score,
            cluster.average_importance,
            cluster.average_abstraction,
        )
        boundary = Boundary(
            id=boundary_id,
            boundary_type=BOUNDARY_MAPPING[cluster.attractor_type],
            status=status_for(boundary_score),
            boundary_score=boundary_score,
            source_cluster_id=cluster.id,
            source_cluster_center=cluster.center,
            target_nodes=list(cluster.member_nodes),
            evidence=list(cluster.supporting_pattern_ids),
            novelty_score=cluster.novelty_score,
            average_importance=cluster.average_importance,
            average_abstraction=cluster.average_abstraction,
            recurrence_factor=cluster.recurrence_factor,
            source_chain=cluster.source_chain.with_id("boundary_ids", boundary_id),
            transformative_score=transformative_score,
            is_transformative=is_transformative,
            notes=[],
        )
        if boundary.status == "confirmed":
            confirmed.append(boundary)
        elif boundary.status == "borderline" and borderline_logs is not None:
            borderline_logs.append(_borderline_log(boundary))
    return confirmed
