from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from so_memory import MemoryFragment, MemoryKernel, MemoryRelation


@dataclass(slots=True)
class BenchmarkCaseResult:
    name: str
    status: str
    observations: dict[str, Any] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


def _bridge_fragment(
    fragment_id: str,
    source: str,
    target: str,
    *,
    content: str | None = None,
    strength: float = 0.85,
    current: bool = False,
) -> MemoryFragment:
    return MemoryFragment(
        id=fragment_id,
        content=content or f"{fragment_id} supplies {source} <-> {target}.",
        labels=[source, target],
        relations=[
            MemoryRelation(
                source,
                target,
                relation_type="bridge",
                strength=strength,
                directed=False,
            )
        ],
        importance=strength,
        persistence=0.8,
        novelty=0.75,
        bridge_potential=strength,
        metadata={"phase": "current"} if current else {},
    )


def _chain_fragment(
    fragment_id: str,
    first: str,
    second: str,
    *,
    support_a: str,
    support_b: str,
) -> MemoryFragment:
    return MemoryFragment(
        id=fragment_id,
        content=f"{fragment_id} supplies {first} -> {second}.",
        labels=[first, second, support_a, support_b],
        relations=[
            MemoryRelation(first, second, relation_type="cause", strength=0.9, directed=True),
            MemoryRelation(support_a, support_b, relation_type="support", strength=0.9, directed=True),
        ],
        importance=0.9,
        persistence=0.8,
        novelty=0.8,
    )


def benchmark_evidence_identity(kernel: MemoryKernel) -> BenchmarkCaseResult:
    one_source_many_contexts = kernel.run(
        [
            _bridge_fragment("bridge_source", "art", "religion", strength=0.9),
            MemoryFragment(id="context_1", content="Weather context.", labels=["weather"]),
            MemoryFragment(id="context_2", content="Food context.", labels=["food"]),
            MemoryFragment(id="context_3", content="Traffic context.", labels=["traffic"]),
        ]
    )
    many_independent_sources = kernel.run(
        [
            _bridge_fragment("source_1", "art", "religion", strength=0.9),
            _bridge_fragment("source_2", "art", "religion", strength=0.85),
            _bridge_fragment("source_3", "art", "religion", strength=0.8),
        ]
    )

    observations = {
        "condition_a_independent_source_count": one_source_many_contexts.evidence_identity.independent_source_count,
        "condition_a_contextual_recurrence_count": one_source_many_contexts.evidence_identity.contextual_recurrence_count,
        "condition_b_independent_source_count": many_independent_sources.evidence_identity.independent_source_count,
        "condition_b_contextual_recurrence_count": many_independent_sources.evidence_identity.contextual_recurrence_count,
    }
    passed = (
        observations["condition_a_independent_source_count"] == 1
        and observations["condition_a_contextual_recurrence_count"] > 1
        and observations["condition_b_independent_source_count"] == 3
    )
    return BenchmarkCaseResult(
        name="evidence_identity",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "condition_a_independent_source_count": 1,
            "condition_a_contextual_recurrence_count": "> 1",
            "condition_b_independent_source_count": 3,
        },
    )


def benchmark_pattern_identity(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            _bridge_fragment("source_1", "art", "religion", strength=0.9),
            _bridge_fragment("source_2", "art", "religion", strength=0.85),
            _bridge_fragment("source_3", "art", "religion", strength=0.8),
        ]
    )
    bridge_groups = [
        group for group in result.pattern_identity_groups if group.pattern_type == "Bridge"
    ]
    observations = {
        "bridge_group_count": len(bridge_groups),
        "bridge_occurrence_count": bridge_groups[0].occurrence_count if bridge_groups else 0,
        "bridge_independent_source_count": bridge_groups[0].independent_source_count if bridge_groups else 0,
    }
    passed = (
        observations["bridge_group_count"] == 1
        and observations["bridge_occurrence_count"] == 3
        and observations["bridge_independent_source_count"] == 3
    )
    return BenchmarkCaseResult(
        name="pattern_identity",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "bridge_group_count": 1,
            "bridge_occurrence_count": 3,
            "bridge_independent_source_count": 3,
        },
    )


def benchmark_direction_preservation(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            _chain_fragment("forward_left", "a", "x", support_a="c", support_b="d"),
            _chain_fragment("forward_right", "x", "b", support_a="e", support_b="f"),
            _chain_fragment("reverse_left", "b", "x", support_a="g", support_b="h"),
            _chain_fragment("reverse_right", "x", "a", support_a="i", support_b="j"),
        ]
    )
    chain_keys = {
        group.identity_key
        for group in result.pattern_identity_groups
        if group.pattern_type == "Chain"
    }
    observations = {
        "chain_identity_group_count": len(chain_keys),
        "has_forward_chain": any("members=a,x,b" in key for key in chain_keys),
        "has_reverse_chain": any("members=b,x,a" in key for key in chain_keys),
    }
    passed = (
        observations["chain_identity_group_count"] >= 2
        and observations["has_forward_chain"]
        and observations["has_reverse_chain"]
    )
    return BenchmarkCaseResult(
        name="direction_preservation",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "chain_identity_group_count": ">= 2",
            "has_forward_chain": True,
            "has_reverse_chain": True,
        },
    )


def benchmark_return_reactivation(kernel: MemoryKernel) -> BenchmarkCaseResult:
    signal = kernel.run(
        [
            _bridge_fragment("past_design", "memory", "structure", strength=0.9),
            _bridge_fragment("current_design", "memory", "structure", strength=0.85, current=True),
        ]
    )
    control = kernel.run(
        [
            _bridge_fragment("past_design", "memory", "structure", strength=0.9),
            _bridge_fragment("current_noise", "coffee", "weather", strength=0.85, current=True),
        ]
    )
    observations = {
        "signal_return_candidate_count": len(signal.return_candidates),
        "control_return_candidate_count": len(control.return_candidates),
        "signal_current_fragment_ids": signal.return_candidates[0].current_fragment_ids if signal.return_candidates else [],
        "signal_past_fragment_ids": signal.return_candidates[0].past_fragment_ids if signal.return_candidates else [],
    }
    passed = (
        observations["signal_return_candidate_count"] >= 1
        and observations["control_return_candidate_count"] == 0
    )
    return BenchmarkCaseResult(
        name="return_reactivation",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "signal_return_candidate_count": ">= 1",
            "control_return_candidate_count": 0,
        },
    )


def benchmark_no_semantic_guessing(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            MemoryFragment(id="past_freedom", content="Past freedom.", labels=["freedom"]),
            MemoryFragment(
                id="current_liberty",
                content="Current liberty.",
                labels=["liberty"],
                metadata={"phase": "current"},
            ),
        ]
    )
    observations = {
        "return_candidate_count": len(result.return_candidates),
        "pattern_identity_group_count": len(result.pattern_identity_groups),
        "labels_remain_distinct": result.structured_json[0]["nodes"][0]["label"] != result.structured_json[1]["nodes"][0]["label"],
    }
    passed = (
        observations["return_candidate_count"] == 0
        and observations["labels_remain_distinct"]
    )
    return BenchmarkCaseResult(
        name="no_semantic_guessing",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "return_candidate_count": 0,
            "labels_remain_distinct": True,
        },
        notes=["The Kernel does not merge freedom and liberty without caller-supplied structure."],
    )


def benchmark_noise_robustness(kernel: MemoryKernel) -> BenchmarkCaseResult:
    noise = [
        MemoryFragment(id=f"noise_{index}", content=f"Noise fragment {label}.", labels=[label])
        for index, label in enumerate(
            ["weather", "food", "traffic", "shopping", "coffee", "sports", "music", "travel"],
            start=1,
        )
    ]
    result = kernel.run(
        [
            _bridge_fragment("past_signal", "memory", "structure", strength=0.9),
            *noise,
            _bridge_fragment("current_signal", "memory", "structure", strength=0.85, current=True),
        ]
    )
    bridge_groups = [
        group
        for group in result.pattern_identity_groups
        if group.pattern_type == "Bridge" and set(group.member_nodes) == {"memory", "structure"}
    ]
    observations = {
        "noise_fragment_count": len(noise),
        "signal_bridge_group_count": len(bridge_groups),
        "return_candidate_count": len(result.return_candidates),
        "false_return_candidates_from_noise": [
            candidate.label
            for candidate in result.return_candidates
            if set(candidate.shared_nodes) != {"memory", "structure"}
        ],
    }
    passed = (
        observations["signal_bridge_group_count"] == 1
        and observations["return_candidate_count"] >= 1
        and observations["false_return_candidates_from_noise"] == []
    )
    return BenchmarkCaseResult(
        name="noise_robustness",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "signal_bridge_group_count": 1,
            "return_candidate_count": ">= 1",
            "false_return_candidates_from_noise": [],
        },
    )


def benchmark_traceability(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            _bridge_fragment("past_trace", "memory", "structure", strength=0.9),
            _bridge_fragment("current_trace", "memory", "structure", strength=0.85, current=True),
        ]
    )
    candidate = result.return_candidates[0] if result.return_candidates else None
    observations = {
        "fragment_id_to_sentence_id_present": bool(result.fragment_id_to_sentence_id),
        "sentence_id_to_fragment_id_present": bool(result.sentence_id_to_fragment_id),
        "pattern_group_source_fragments_present": bool(result.pattern_identity_groups and result.pattern_identity_groups[0].source_fragment_ids),
        "return_current_fragments_present": bool(candidate and candidate.current_fragment_ids),
        "return_past_fragments_present": bool(candidate and candidate.past_fragment_ids),
    }
    passed = all(observations.values())
    return BenchmarkCaseResult(
        name="traceability",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={key: True for key in observations},
    )


def benchmark_agent_memory_trace(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            _bridge_fragment("past_failure", "tool_permission", "missing_approval", strength=0.9),
            _bridge_fragment("past_retry", "tool_permission", "missing_approval", strength=0.85),
            _bridge_fragment(
                "current_action",
                "tool_permission",
                "missing_approval",
                strength=0.8,
                current=True,
            ),
        ]
    )
    observations = {
        "pattern_identity_group_count": len(result.pattern_identity_groups),
        "return_candidate_count": len(result.return_candidates),
        "current_fragment_ids": result.return_candidates[0].current_fragment_ids if result.return_candidates else [],
        "past_fragment_ids": result.return_candidates[0].past_fragment_ids if result.return_candidates else [],
    }
    passed = (
        observations["pattern_identity_group_count"] >= 1
        and observations["return_candidate_count"] >= 1
        and observations["current_fragment_ids"] == ["current_action"]
    )
    return BenchmarkCaseResult(
        name="agent_memory_trace",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "pattern_identity_group_count": ">= 1",
            "return_candidate_count": ">= 1",
            "current_fragment_ids": ["current_action"],
        },
    )


def benchmark_workflow_blocker_recurrence(kernel: MemoryKernel) -> BenchmarkCaseResult:
    result = kernel.run(
        [
            _bridge_fragment("past_api_blocker", "blocked_export", "schema_migration", strength=0.9),
            _bridge_fragment("past_ui_blocker", "blocked_export", "schema_migration", strength=0.85),
            _bridge_fragment(
                "current_report_blocker",
                "blocked_export",
                "schema_migration",
                strength=0.8,
                current=True,
            ),
        ]
    )
    bridge_groups = [group for group in result.pattern_identity_groups if group.pattern_type == "Bridge"]
    observations = {
        "bridge_group_count": len(bridge_groups),
        "independent_source_count": bridge_groups[0].independent_source_count if bridge_groups else 0,
        "return_candidate_count": len(result.return_candidates),
    }
    passed = (
        observations["bridge_group_count"] == 1
        and observations["independent_source_count"] == 3
        and observations["return_candidate_count"] == 1
    )
    return BenchmarkCaseResult(
        name="workflow_blocker_recurrence",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "bridge_group_count": 1,
            "independent_source_count": 3,
            "return_candidate_count": 1,
        },
    )


def benchmark_rag_trace_evidence(kernel: MemoryKernel) -> BenchmarkCaseResult:
    def retrieved_claim(fragment_id: str, source_id: str, current: bool = False) -> MemoryFragment:
        return MemoryFragment(
            id=fragment_id,
            content=f"rag_trace: {source_id} supports policy claim",
            labels=["policy_claim", "evidence_source"],
            relations=[
                MemoryRelation(
                    "policy_claim",
                    "evidence_source",
                    relation_type="support",
                    strength=0.85,
                    directed=True,
                )
            ],
            memory_type="rag_trace",
            source_id=source_id,
            importance=0.85,
            persistence=0.75,
            novelty=0.65,
            metadata={"phase": "current"} if current else {},
        )

    result = kernel.run(
        [
            retrieved_claim("chunk_a", "document_a"),
            retrieved_claim("chunk_b", "document_b"),
            retrieved_claim("chunk_c_repeat", "document_a"),
            retrieved_claim("current_chunk", "document_c", current=True),
        ]
    )
    star_groups = [group for group in result.pattern_identity_groups if group.pattern_type == "Star"]
    observations = {
        "independent_source_count": result.evidence_identity.independent_source_count,
        "contextual_recurrence_count": result.evidence_identity.contextual_recurrence_count,
        "star_group_count": len(star_groups),
        "return_candidate_count": len(result.return_candidates),
    }
    passed = (
        observations["independent_source_count"] == 4
        and observations["contextual_recurrence_count"] >= 1
        and observations["star_group_count"] >= 1
        and observations["return_candidate_count"] >= 1
    )
    return BenchmarkCaseResult(
        name="rag_trace_evidence",
        status="PASS" if passed else "FAIL",
        observations=observations,
        expected={
            "independent_source_count": 4,
            "contextual_recurrence_count": ">= 1",
            "star_group_count": ">= 1",
            "return_candidate_count": ">= 1",
        },
    )


BENCHMARK_CASES: list[Callable[[MemoryKernel], BenchmarkCaseResult]] = [
    benchmark_evidence_identity,
    benchmark_pattern_identity,
    benchmark_direction_preservation,
    benchmark_return_reactivation,
    benchmark_no_semantic_guessing,
    benchmark_noise_robustness,
    benchmark_traceability,
    benchmark_agent_memory_trace,
    benchmark_workflow_blocker_recurrence,
    benchmark_rag_trace_evidence,
]
