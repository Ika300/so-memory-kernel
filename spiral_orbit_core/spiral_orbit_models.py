from __future__ import annotations

from dataclasses import dataclass, field

from spiral_orbit_validation import (
    ATTRACTOR_TYPES,
    BOUNDARY_TYPES,
    CURIOSITY_TYPES,
    NODE_TYPES,
    PATTERN_TYPES,
    RELATION_TYPES,
    STATUSES,
    TARGET_TYPES,
    preserve_first_seen,
    validate_allowed,
    validate_node_id,
    validate_unit_score,
    validate_valence,
)


@dataclass(slots=True)
class SourceChain:
    sentence_ids: list[str] = field(default_factory=list)
    microtopology_ids: list[str] = field(default_factory=list)
    overlay_ids: list[str] = field(default_factory=list)
    independent_source_sentence_ids: list[str] = field(default_factory=list)
    independent_source_microtopology_ids: list[str] = field(default_factory=list)
    contextual_recurrence_overlay_ids: list[str] = field(default_factory=list)
    pattern_ids: list[str] = field(default_factory=list)
    cluster_ids: list[str] = field(default_factory=list)
    boundary_ids: list[str] = field(default_factory=list)
    curiosity_ids: list[str] = field(default_factory=list)
    exploration_target_ids: list[str] = field(default_factory=list)
    insight_json_ids: list[str] = field(default_factory=list)

    @classmethod
    def merge(cls, *chains: SourceChain) -> SourceChain:
        return cls(
            sentence_ids=preserve_first_seen(
                value for chain in chains for value in chain.sentence_ids
            ),
            microtopology_ids=preserve_first_seen(
                value for chain in chains for value in chain.microtopology_ids
            ),
            overlay_ids=preserve_first_seen(
                value for chain in chains for value in chain.overlay_ids
            ),
            independent_source_sentence_ids=preserve_first_seen(
                value
                for chain in chains
                for value in chain.independent_source_sentence_ids
            ),
            independent_source_microtopology_ids=preserve_first_seen(
                value
                for chain in chains
                for value in chain.independent_source_microtopology_ids
            ),
            contextual_recurrence_overlay_ids=preserve_first_seen(
                value
                for chain in chains
                for value in chain.contextual_recurrence_overlay_ids
            ),
            pattern_ids=preserve_first_seen(
                value for chain in chains for value in chain.pattern_ids
            ),
            cluster_ids=preserve_first_seen(
                value for chain in chains for value in chain.cluster_ids
            ),
            boundary_ids=preserve_first_seen(
                value for chain in chains for value in chain.boundary_ids
            ),
            curiosity_ids=preserve_first_seen(
                value for chain in chains for value in chain.curiosity_ids
            ),
            exploration_target_ids=preserve_first_seen(
                value
                for chain in chains
                for value in chain.exploration_target_ids
            ),
            insight_json_ids=preserve_first_seen(
                value for chain in chains for value in chain.insight_json_ids
            ),
        )

    def with_id(self, field_name: str, object_id: str) -> SourceChain:
        merged = SourceChain.merge(self)
        values = getattr(merged, field_name)
        setattr(merged, field_name, preserve_first_seen([*values, object_id]))
        return merged

    def with_evidence_history(
        self,
        *,
        independent_source_sentence_ids: list[str],
        independent_source_microtopology_ids: list[str],
        contextual_recurrence_overlay_ids: list[str],
    ) -> SourceChain:
        evidence = SourceChain(
            independent_source_sentence_ids=independent_source_sentence_ids,
            independent_source_microtopology_ids=independent_source_microtopology_ids,
            contextual_recurrence_overlay_ids=contextual_recurrence_overlay_ids,
        )
        return SourceChain.merge(self, evidence)


@dataclass(slots=True)
class NodeFeature:
    id: str
    label: str
    node_type: str
    importance: float
    persistence: float
    valence: float
    arousal: float
    certainty: float
    novelty: float
    abstraction: float

    def __post_init__(self) -> None:
        validate_node_id(self.id)
        validate_allowed("node_type", self.node_type, NODE_TYPES)
        validate_unit_score("importance", self.importance)
        validate_unit_score("persistence", self.persistence)
        validate_valence(self.valence)
        validate_unit_score("arousal", self.arousal)
        validate_unit_score("certainty", self.certainty)
        validate_unit_score("novelty", self.novelty)
        validate_unit_score("abstraction", self.abstraction)


@dataclass(slots=True)
class EdgeFeature:
    source: str
    target: str
    relation_type: str
    strength: float
    directed: bool

    def __post_init__(self) -> None:
        validate_allowed("relation_type", self.relation_type, RELATION_TYPES)
        validate_unit_score("strength", self.strength)


@dataclass(slots=True)
class EdgeRecord:
    source: str
    target: str
    relation_type: str
    strength: float
    directed: bool
    synthetic: bool
    source_microtopology_ids: list[str]

    def __post_init__(self) -> None:
        validate_allowed("relation_type", self.relation_type, RELATION_TYPES)
        validate_unit_score("strength", self.strength)


@dataclass(slots=True)
class GlobalScores:
    importance: float
    persistence: float
    valence: float
    arousal: float
    certainty: float
    novelty: float
    bridge_potential: float
    tension_score: float
    gap_score: float

    def __post_init__(self) -> None:
        validate_unit_score("importance", self.importance)
        validate_unit_score("persistence", self.persistence)
        validate_valence(self.valence)
        validate_unit_score("arousal", self.arousal)
        validate_unit_score("certainty", self.certainty)
        validate_unit_score("novelty", self.novelty)
        validate_unit_score("bridge_potential", self.bridge_potential)
        validate_unit_score("tension_score", self.tension_score)
        validate_unit_score("gap_score", self.gap_score)


@dataclass(slots=True)
class MicroTopology:
    id: str
    raw_text: str
    nodes: list[NodeFeature]
    edges: list[EdgeFeature]
    scores: GlobalScores
    categories: list[str]
    source_chain: SourceChain
    notes: list[str]


@dataclass(slots=True)
class OverlayResult:
    id: str
    source_microtopology_ids: list[str]
    all_edge_records: list[EdgeRecord]
    shared_centers: list[str]
    star_centers: list[str]
    shared_nodes: list[str]
    shared_relation_types: list[str]
    connected_chain_nodes: list[str]
    chain_paths: list[list[str]]
    tension_edges: list[EdgeRecord]
    bridge_edges: list[EdgeRecord]
    bridge_pairs: list[list[str]]
    gap_nodes: list[str]
    gap_node_importance: dict[str, float]
    novelty_score: float
    support_strength: float
    cause_strength: float
    contrast_strength: float
    bridge_strength: float
    average_gap_score: float
    average_importance: float
    average_abstraction: float
    overlap_strength: float
    source_chain: SourceChain
    notes: list[str]

    def __post_init__(self) -> None:
        for name in (
            "novelty_score",
            "support_strength",
            "cause_strength",
            "contrast_strength",
            "bridge_strength",
            "average_gap_score",
            "average_importance",
            "average_abstraction",
            "overlap_strength",
        ):
            validate_unit_score(name, getattr(self, name))


@dataclass(slots=True)
class Pattern:
    id: str
    pattern_type: str
    status: str
    strength_score: float
    center_candidate: str
    source_nodes: list[str]
    target_nodes: list[str]
    member_nodes: list[str]
    member_edges: list[EdgeRecord]
    node_importance_map: dict[str, float]
    source_overlay_ids: list[str]
    novelty_score: float
    average_importance: float
    average_abstraction: float
    source_chain: SourceChain
    transformative_score: float
    is_transformative: bool
    notes: list[str]

    def __post_init__(self) -> None:
        validate_allowed("pattern_type", self.pattern_type, PATTERN_TYPES)
        validate_allowed("status", self.status, STATUSES)
        validate_unit_score("strength_score", self.strength_score)
        validate_unit_score("novelty_score", self.novelty_score)
        validate_unit_score("average_importance", self.average_importance)
        validate_unit_score("average_abstraction", self.average_abstraction)
        validate_unit_score("transformative_score", self.transformative_score)


@dataclass(slots=True)
class AttractorCluster:
    id: str
    center: str
    attractor_type: str
    status: str
    cluster_score: float
    supporting_pattern_ids: list[str]
    supporting_pattern_types: list[str]
    member_nodes: list[str]
    member_edges: list[EdgeRecord]
    novelty_score: float
    average_importance: float
    average_abstraction: float
    recurrence_factor: float
    pattern_count_factor: float
    member_factor: float
    source_chain: SourceChain
    transformative_score: float
    is_transformative: bool
    notes: list[str]

    def __post_init__(self) -> None:
        validate_allowed("attractor_type", self.attractor_type, ATTRACTOR_TYPES)
        validate_allowed("status", self.status, STATUSES)
        for name in (
            "cluster_score",
            "novelty_score",
            "average_importance",
            "average_abstraction",
            "recurrence_factor",
            "pattern_count_factor",
            "member_factor",
            "transformative_score",
        ):
            validate_unit_score(name, getattr(self, name))


@dataclass(slots=True)
class Boundary:
    id: str
    boundary_type: str
    status: str
    boundary_score: float
    source_cluster_id: str
    source_cluster_center: str
    target_nodes: list[str]
    evidence: list[str]
    novelty_score: float
    average_importance: float
    average_abstraction: float
    recurrence_factor: float
    source_chain: SourceChain
    transformative_score: float
    is_transformative: bool
    notes: list[str]

    def __post_init__(self) -> None:
        validate_allowed("boundary_type", self.boundary_type, BOUNDARY_TYPES)
        validate_allowed("status", self.status, STATUSES)
        for name in (
            "boundary_score",
            "novelty_score",
            "average_importance",
            "average_abstraction",
            "recurrence_factor",
            "transformative_score",
        ):
            validate_unit_score(name, getattr(self, name))


@dataclass(slots=True)
class Curiosity:
    id: str
    curiosity_type: str
    status: str
    curiosity_score: float
    source_boundary_id: str
    source_boundary_type: str
    target_candidates: list[str]
    novelty_score: float
    average_importance: float
    average_abstraction: float
    recurrence_factor: float
    source_chain: SourceChain
    transformative_score: float
    is_transformative: bool
    notes: list[str]

    def __post_init__(self) -> None:
        validate_allowed("curiosity_type", self.curiosity_type, CURIOSITY_TYPES)
        validate_allowed("status", self.status, STATUSES)
        for name in (
            "curiosity_score",
            "novelty_score",
            "average_importance",
            "average_abstraction",
            "recurrence_factor",
            "transformative_score",
        ):
            validate_unit_score(name, getattr(self, name))


@dataclass(slots=True)
class ExplorationTarget:
    id: str
    target_type: str
    status: str
    priority_score: float
    target_nodes: list[str]
    exploration_direction: str
    source_curiosity_ids: list[str]
    novelty_score: float
    average_importance: float
    average_abstraction: float
    source_chain: SourceChain
    transformative_score: float
    is_transformative: bool
    notes: list[str]

    def __post_init__(self) -> None:
        validate_allowed("target_type", self.target_type, TARGET_TYPES)
        validate_allowed("status", self.status, STATUSES)
        for name in (
            "priority_score",
            "novelty_score",
            "average_importance",
            "average_abstraction",
            "transformative_score",
        ):
            validate_unit_score(name, getattr(self, name))


@dataclass(slots=True)
class QuestionSeed:
    question_type: str
    target_nodes: list[str]
    direction: str
    confidence: float
    priority: float

    def __post_init__(self) -> None:
        validate_unit_score("confidence", self.confidence)
        validate_unit_score("priority", self.priority)


@dataclass(slots=True)
class IdeaSeed:
    idea_type: str
    target_nodes: list[str]
    connection_candidates: list[str]
    confidence: float
    priority: float

    def __post_init__(self) -> None:
        validate_unit_score("confidence", self.confidence)
        validate_unit_score("priority", self.priority)


@dataclass(slots=True)
class SuggestionSeed:
    suggestion_type: str
    target_nodes: list[str]
    action_type: str
    confidence: float
    priority: float

    def __post_init__(self) -> None:
        validate_unit_score("confidence", self.confidence)
        validate_unit_score("priority", self.priority)


@dataclass(slots=True)
class InsightJSON:
    id: str
    source_exploration_target_ids: list[str]
    questions: list[QuestionSeed]
    ideas: list[IdeaSeed]
    suggestions: list[SuggestionSeed]
    confidence: float
    priority: float
    source_chain: SourceChain
    notes: list[str]

    def __post_init__(self) -> None:
        validate_unit_score("confidence", self.confidence)
        validate_unit_score("priority", self.priority)
