from __future__ import annotations

from spiral_orbit_models import (
    ExplorationTarget,
    IdeaSeed,
    InsightJSON,
    QuestionSeed,
    SourceChain,
    SuggestionSeed,
)
from spiral_orbit_validation import average, maximum


def generate_insight_json(
    targets: list[ExplorationTarget],
) -> InsightJSON | None:
    if not targets:
        return None

    insight_id = "ij_001"
    questions: list[QuestionSeed] = []
    ideas: list[IdeaSeed] = []
    suggestions: list[SuggestionSeed] = []

    for target in targets:
        common = {
            "target_nodes": list(target.target_nodes),
            "confidence": target.priority_score,
            "priority": target.priority_score,
        }
        questions.append(
            QuestionSeed(
                question_type=target.target_type,
                direction=target.exploration_direction,
                **common,
            )
        )
        if target.target_type == "MissingInformation":
            suggestions.append(
                SuggestionSeed(
                    suggestion_type="Example",
                    action_type="Observe",
                    **common,
                )
            )
        elif target.target_type == "ConflictResolution":
            suggestions.append(
                SuggestionSeed(
                    suggestion_type="Alternative",
                    action_type="Reflect",
                    **common,
                )
            )
        elif target.target_type == "NewConnection":
            ideas.append(
                IdeaSeed(
                    idea_type="Bridge",
                    connection_candidates=list(target.target_nodes),
                    **common,
                )
            )
            suggestions.append(
                SuggestionSeed(
                    suggestion_type="NeighboringDomain",
                    action_type="Connect",
                    **common,
                )
            )
        else:
            ideas.append(
                IdeaSeed(
                    idea_type="Expansion",
                    connection_candidates=list(target.target_nodes),
                    **common,
                )
            )
            suggestions.append(
                SuggestionSeed(
                    suggestion_type="Example",
                    action_type="Explore",
                    **common,
                )
            )

    source_chain = SourceChain.merge(
        *(target.source_chain for target in targets)
    ).with_id("insight_json_ids", insight_id)
    return InsightJSON(
        id=insight_id,
        source_exploration_target_ids=[target.id for target in targets],
        questions=questions,
        ideas=ideas,
        suggestions=suggestions,
        confidence=float(average(target.priority_score for target in targets)),
        priority=float(maximum(target.priority_score for target in targets)),
        source_chain=source_chain,
        notes=[],
    )
