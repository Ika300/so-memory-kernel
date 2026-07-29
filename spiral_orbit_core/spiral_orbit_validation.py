from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T")

NODE_TYPES = frozenset(
    {"entity", "concept", "emotion", "value", "action", "state", "domain"}
)
RELATION_TYPES = frozenset(
    {
        "support",
        "cause",
        "contrast",
        "tension",
        "bridge",
        "association",
        "dependency",
    }
)
PATTERN_TYPES = frozenset({"Star", "Chain", "Tension", "Bridge", "Gap"})
ATTRACTOR_TYPES = frozenset({"StarChain", "Tension", "Bridge", "Gap"})
BOUNDARY_TYPES = frozenset(
    {"GapBoundary", "TensionBoundary", "BridgeBoundary", "ExpansionBoundary"}
)
CURIOSITY_TYPES = frozenset(
    {"GapCuriosity", "TensionCuriosity", "BridgeCuriosity", "ExpansionCuriosity"}
)
TARGET_TYPES = frozenset(
    {"MissingInformation", "ConflictResolution", "NewConnection", "Expansion"}
)
STATUSES = frozenset({"confirmed", "borderline", "rejected"})

SENTENCE_ID_PATTERN = re.compile(r"^s\d{3}$")
NODE_ID_PATTERN = re.compile(r"^nd_\d{3}_\d{3}$")


class SpiralOrbitValidationError(ValueError):
    pass


def require_float(name: str, value: object) -> float:
    if not isinstance(value, float):
        raise SpiralOrbitValidationError(f"{name} must be a float")
    return value


def validate_unit_score(name: str, value: object) -> float:
    score = require_float(name, value)
    if not 0.0 <= score <= 1.0:
        raise SpiralOrbitValidationError(f"{name} must be from 0.0 to 1.0")
    return score


def validate_valence(value: object) -> float:
    valence = require_float("valence", value)
    if not -1.0 <= valence <= 1.0:
        raise SpiralOrbitValidationError("valence must be from -1.0 to 1.0")
    return valence


def validate_allowed(name: str, value: str, allowed: frozenset[str]) -> str:
    if value not in allowed:
        raise SpiralOrbitValidationError(f"{name} has unsupported value: {value}")
    return value


def validate_sentence_id(value: str) -> str:
    if not SENTENCE_ID_PATTERN.fullmatch(value):
        raise SpiralOrbitValidationError("sentence_id must match s001, s002, s003, ...")
    return value


def validate_node_id(value: str) -> str:
    if not NODE_ID_PATTERN.fullmatch(value):
        raise SpiralOrbitValidationError(
            "NodeFeature.id must match nd_<microtopology_number>_<node_number>"
        )
    return value


def normalize_label(value: str) -> str:
    return " ".join(value.strip().lower().split())


def preserve_first_seen(values: Iterable[T]) -> list[T]:
    result: list[T] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def average(values: Iterable[float], fallback: float = 0.0) -> float:
    materialized = list(values)
    if not materialized:
        return fallback
    return sum(materialized) / len(materialized)


def maximum(values: Iterable[float], fallback: float = 0.0) -> float:
    materialized = list(values)
    if not materialized:
        return fallback
    return max(materialized)


def status_for(score: float) -> str:
    validate_unit_score("status score", score)
    if score >= 0.70:
        return "confirmed"
    if score >= 0.55:
        return "borderline"
    return "rejected"


def transformative(
    novelty_score: float | None,
    average_importance: float | None,
    average_abstraction: float | None,
) -> tuple[float, bool]:
    novelty = 0.5 if novelty_score is None else novelty_score
    importance = 0.5 if average_importance is None else average_importance
    abstraction = 0.5 if average_abstraction is None else average_abstraction
    score = (0.50 * novelty) + (0.30 * importance) + (0.20 * abstraction)
    validate_unit_score("transformative_score", float(score))
    return float(score), score >= 0.70
