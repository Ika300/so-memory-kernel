from __future__ import annotations

from spiral_orbit_models import Boundary, Curiosity
from spiral_orbit_validation import status_for, transformative


CURIOSITY_MAPPING = {
    "GapBoundary": "GapCuriosity",
    "TensionBoundary": "TensionCuriosity",
    "BridgeBoundary": "BridgeCuriosity",
    "ExpansionBoundary": "ExpansionCuriosity",
}


def _score(boundary: Boundary) -> float:
    if boundary.boundary_type in {"GapBoundary", "TensionBoundary"}:
        return boundary.boundary_score
    if boundary.boundary_type == "BridgeBoundary":
        return (0.80 * boundary.boundary_score) + (
            0.20 * boundary.novelty_score
        )
    return (0.70 * boundary.boundary_score) + (
        0.30 * boundary.recurrence_factor
    )


def _borderline_log(curiosity: Curiosity) -> str:
    return (
        f"[Curiosity] id={curiosity.id} type={curiosity.curiosity_type} "
        f"score={curiosity.curiosity_score} source_chain={curiosity.source_chain}"
    )


def generate_curiosities(
    boundaries: list[Boundary], borderline_logs: list[str] | None = None
) -> list[Curiosity]:
    confirmed: list[Curiosity] = []
    for index, boundary in enumerate(boundaries, start=1):
        curiosity_id = f"cu_{index:03d}"
        curiosity_score = float(_score(boundary))
        transformative_score, is_transformative = transformative(
            boundary.novelty_score,
            boundary.average_importance,
            boundary.average_abstraction,
        )
        curiosity = Curiosity(
            id=curiosity_id,
            curiosity_type=CURIOSITY_MAPPING[boundary.boundary_type],
            status=status_for(curiosity_score),
            curiosity_score=curiosity_score,
            source_boundary_id=boundary.id,
            source_boundary_type=boundary.boundary_type,
            target_candidates=list(boundary.target_nodes),
            novelty_score=boundary.novelty_score,
            average_importance=boundary.average_importance,
            average_abstraction=boundary.average_abstraction,
            recurrence_factor=boundary.recurrence_factor,
            source_chain=boundary.source_chain.with_id(
                "curiosity_ids", curiosity_id
            ),
            transformative_score=transformative_score,
            is_transformative=is_transformative,
            notes=[],
        )
        if curiosity.status == "confirmed":
            confirmed.append(curiosity)
        elif curiosity.status == "borderline" and borderline_logs is not None:
            borderline_logs.append(_borderline_log(curiosity))
    return confirmed
