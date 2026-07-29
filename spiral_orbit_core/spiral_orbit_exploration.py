from __future__ import annotations

from spiral_orbit_models import Curiosity, ExplorationTarget
from spiral_orbit_validation import preserve_first_seen, status_for, transformative


TARGET_MAPPING = {
    "GapCuriosity": ("MissingInformation", "Find missing node"),
    "TensionCuriosity": ("ConflictResolution", "Resolve contradiction"),
    "BridgeCuriosity": ("NewConnection", "Search neighboring domain"),
    "ExpansionCuriosity": ("Expansion", "Extend attractor"),
}


def _borderline_log(target: ExplorationTarget) -> str:
    return (
        f"[ExplorationTarget] id={target.id} type={target.target_type} "
        f"score={target.priority_score} source_chain={target.source_chain}"
    )


def generate_exploration_targets(
    curiosities: list[Curiosity], borderline_logs: list[str] | None = None
) -> list[ExplorationTarget]:
    confirmed: list[ExplorationTarget] = []
    for index, curiosity in enumerate(curiosities, start=1):
        target_id = f"et_{index:03d}"
        target_type, direction = TARGET_MAPPING[curiosity.curiosity_type]
        priority_score = float(
            (0.60 * curiosity.curiosity_score)
            + (0.40 * curiosity.novelty_score)
        )
        transformative_score, is_transformative = transformative(
            curiosity.novelty_score,
            curiosity.average_importance,
            curiosity.average_abstraction,
        )
        target = ExplorationTarget(
            id=target_id,
            target_type=target_type,
            status=status_for(priority_score),
            priority_score=priority_score,
            target_nodes=preserve_first_seen(curiosity.target_candidates),
            exploration_direction=direction,
            source_curiosity_ids=[curiosity.id],
            novelty_score=curiosity.novelty_score,
            average_importance=curiosity.average_importance,
            average_abstraction=curiosity.average_abstraction,
            source_chain=curiosity.source_chain.with_id(
                "exploration_target_ids", target_id
            ),
            transformative_score=transformative_score,
            is_transformative=is_transformative,
            notes=[],
        )
        if target.status == "confirmed":
            confirmed.append(target)
        elif target.status == "borderline" and borderline_logs is not None:
            borderline_logs.append(_borderline_log(target))
    return confirmed
