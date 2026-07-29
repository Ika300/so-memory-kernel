from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


NODE_TYPES = frozenset({"entity", "concept", "emotion", "value", "action", "state", "domain"})
RELATION_TYPES = frozenset({"support", "cause", "contrast", "tension", "bridge", "association", "dependency"})


class MemoryKernelValidationError(ValueError):
    """Raised when Memory Kernel input cannot be safely converted to SO Core input."""


def _require_unit_score(name: str, value: float) -> float:
    if not isinstance(value, float):
        raise MemoryKernelValidationError(f"{name} must be a float")
    if not 0.0 <= value <= 1.0:
        raise MemoryKernelValidationError(f"{name} must be from 0.0 to 1.0")
    return value


def _require_valence(value: float) -> float:
    if not isinstance(value, float):
        raise MemoryKernelValidationError("valence must be a float")
    if not -1.0 <= value <= 1.0:
        raise MemoryKernelValidationError("valence must be from -1.0 to 1.0")
    return value


def _require_non_empty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MemoryKernelValidationError(f"{name} must be a non-empty string")
    return value


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class MemoryRelation:
    """A caller-supplied structural relation between two memory labels.

    The Kernel does not infer this relation from language. It only preserves and
    forwards caller-provided structure into the copied Spiral Orbit Core.
    """

    source: str
    target: str
    relation_type: str = "association"
    strength: float = 0.5
    directed: bool = True

    def __post_init__(self) -> None:
        self.source = _require_non_empty("source", self.source)
        self.target = _require_non_empty("target", self.target)
        if self.relation_type not in RELATION_TYPES:
            raise MemoryKernelValidationError(f"relation_type has unsupported value: {self.relation_type}")
        _require_unit_score("strength", self.strength)


@dataclass(slots=True)
class MemoryFragment:
    """A minimal unit of structural memory.

    `content` is retained as trace text. `labels` are structural anchors supplied
    by the caller. If no labels are supplied, the content itself is preserved as
    a single node label; no semantic dictionary or parser is applied.
    """

    id: str
    content: str
    labels: list[str] = field(default_factory=list)
    relations: list[MemoryRelation] = field(default_factory=list)
    memory_type: str = "observation"
    space_id: str = "default"
    importance: float = 0.5
    persistence: float = 0.5
    valence: float = 0.0
    arousal: float = 0.5
    certainty: float = 0.5
    novelty: float = 0.5
    abstraction: float = 0.5
    bridge_potential: float = 0.0
    tension_score: float = 0.0
    gap_score: float = 0.0
    node_type: str = "concept"
    source_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.id = _require_non_empty("id", self.id)
        self.content = _require_non_empty("content", self.content)
        self.space_id = _require_non_empty("space_id", self.space_id)
        if self.node_type not in NODE_TYPES:
            raise MemoryKernelValidationError(f"node_type has unsupported value: {self.node_type}")
        _require_unit_score("importance", self.importance)
        _require_unit_score("persistence", self.persistence)
        _require_valence(self.valence)
        _require_unit_score("arousal", self.arousal)
        _require_unit_score("certainty", self.certainty)
        _require_unit_score("novelty", self.novelty)
        _require_unit_score("abstraction", self.abstraction)
        _require_unit_score("bridge_potential", self.bridge_potential)
        _require_unit_score("tension_score", self.tension_score)
        _require_unit_score("gap_score", self.gap_score)
        cleaned_labels = []
        for label in self.labels:
            cleaned = _require_non_empty("label", label).strip()
            if cleaned not in cleaned_labels:
                cleaned_labels.append(cleaned)
        self.labels = cleaned_labels

    @property
    def structural_labels(self) -> list[str]:
        return self.labels if self.labels else [self.content]


@dataclass(slots=True)
class MemoryInput:
    fragments: list[MemoryFragment]

    def __post_init__(self) -> None:
        if not self.fragments:
            raise MemoryKernelValidationError("MemoryInput.fragments must not be empty")
        seen: set[str] = set()
        for fragment in self.fragments:
            if fragment.id in seen:
                raise MemoryKernelValidationError(f"MemoryFragment.id must be unique: {fragment.id}")
            seen.add(fragment.id)


@dataclass(slots=True)
class EvidenceIdentity:
    """Evidence history exposed by the Memory Kernel without changing SO Core behavior."""

    independent_source_sentence_ids: list[str] = field(default_factory=list)
    independent_source_fragment_ids: list[str] = field(default_factory=list)
    independent_source_microtopology_ids: list[str] = field(default_factory=list)
    contextual_recurrence_overlay_ids: list[str] = field(default_factory=list)

    @property
    def independent_source_count(self) -> int:
        return len(self.independent_source_sentence_ids)

    @property
    def contextual_recurrence_count(self) -> int:
        return len(self.contextual_recurrence_overlay_ids)


@dataclass(slots=True)
class PatternIdentity:
    """Exact structural identity for a Core Pattern.

    This is a trace object, not a merge instruction. Matching identity keys mean
    exact structural recurrence under the current Core output, not semantic
    equivalence.
    """

    identity_key: str
    pattern_id: str
    pattern_type: str
    center_candidate: str
    member_nodes: list[str]
    source_fragment_ids: list[str]
    source_sentence_ids: list[str]
    source_overlay_ids: list[str]
    contextual_recurrence_overlay_ids: list[str]


@dataclass(slots=True)
class PatternIdentityGroup:
    """A group of Patterns sharing the same exact structural identity key."""

    identity_key: str
    pattern_type: str
    pattern_ids: list[str]
    center_candidate: str
    member_nodes: list[str]
    source_fragment_ids: list[str]
    source_sentence_ids: list[str]
    contextual_recurrence_overlay_ids: list[str]

    @property
    def occurrence_count(self) -> int:
        return len(self.pattern_ids)

    @property
    def independent_source_count(self) -> int:
        return len(self.source_sentence_ids)

    @property
    def contextual_recurrence_count(self) -> int:
        return len(self.contextual_recurrence_overlay_ids)


@dataclass(slots=True)
class ReturnCandidate:
    """Transient structural re-activation candidate.

    Return is not search and not semantic similarity. A candidate appears when a
    current fragment re-touches an exact or partially overlapping structural
    identity that has prior evidence in the same run.
    """

    label: str
    return_score: float
    current_fragment_ids: list[str]
    past_fragment_ids: list[str]
    shared_pattern_identity_keys: list[str]
    shared_nodes: list[str]
    connection_reason: str
    caution: str = "Return candidate only; not a conclusion."

    def __post_init__(self) -> None:
        _require_unit_score("return_score", self.return_score)


@dataclass(slots=True)
class MemoryKernelResult:
    """Public SDK result wrapper around the frozen Spiral Orbit Core output."""

    insight: Any
    structured_json: list[dict[str, Any]]
    fragment_id_to_sentence_id: dict[str, str]
    sentence_id_to_fragment_id: dict[str, str]
    evidence_identity: EvidenceIdentity = field(default_factory=EvidenceIdentity)
    pattern_identities: list[PatternIdentity] = field(default_factory=list)
    pattern_identity_groups: list[PatternIdentityGroup] = field(default_factory=list)
    return_candidates: list[ReturnCandidate] = field(default_factory=list)

    @property
    def has_insight(self) -> bool:
        return self.insight is not None
