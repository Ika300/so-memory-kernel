from __future__ import annotations

from .models import MemoryFragment, PatternIdentityGroup, ReturnCandidate


def _preserve_first_seen(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _current_fragment_ids(fragments: list[MemoryFragment]) -> list[str]:
    return [
        fragment.id
        for fragment in fragments
        if fragment.metadata.get("phase") == "current"
    ]


def _past_fragment_ids(fragments: list[MemoryFragment], current_ids: list[str]) -> list[str]:
    current = set(current_ids)
    return [fragment.id for fragment in fragments if fragment.id not in current]


def _score(
    *,
    exact_identity_reused: bool,
    shared_node_count: int,
    current_evidence_count: int,
    past_evidence_count: int,
) -> float:
    score = 0.0
    if exact_identity_reused:
        score += 0.55
    score += min(shared_node_count, 3) * 0.10
    score += min(current_evidence_count, 2) * 0.05
    score += min(past_evidence_count, 2) * 0.05
    return float(min(score, 1.0))


def return_candidates_from_pattern_groups(
    pattern_identity_groups: list[PatternIdentityGroup],
    fragments: list[MemoryFragment],
) -> list[ReturnCandidate]:
    """Create transient Return candidates from current/past structural contact.

    This is not semantic search. It only considers exact Pattern Identity groups
    and node overlap already produced by the Core run. It does not persist,
    retrieve from storage, or merge identities.
    """

    current_ids = _current_fragment_ids(fragments)
    if not current_ids:
        return []

    past_ids = _past_fragment_ids(fragments, current_ids)
    if not past_ids:
        return []

    current = set(current_ids)
    past = set(past_ids)
    candidates: list[ReturnCandidate] = []

    for group in pattern_identity_groups:
        group_sources = set(group.source_fragment_ids)
        current_sources = _preserve_first_seen(
            [fragment_id for fragment_id in group.source_fragment_ids if fragment_id in current]
        )
        past_sources = _preserve_first_seen(
            [fragment_id for fragment_id in group.source_fragment_ids if fragment_id in past]
        )
        if not current_sources or not past_sources:
            continue

        shared_nodes = list(group.member_nodes)
        exact_identity_reused = bool(group_sources & current and group_sources & past)
        return_score = _score(
            exact_identity_reused=exact_identity_reused,
            shared_node_count=len(shared_nodes),
            current_evidence_count=len(current_sources),
            past_evidence_count=len(past_sources),
        )
        candidates.append(
            ReturnCandidate(
                label=f"{group.pattern_type}:{group.center_candidate}",
                return_score=return_score,
                current_fragment_ids=current_sources,
                past_fragment_ids=past_sources,
                shared_pattern_identity_keys=[group.identity_key],
                shared_nodes=shared_nodes,
                connection_reason=(
                    "A current fragment and prior fragment share the same exact "
                    "Pattern Identity under the Core output."
                ),
            )
        )

    candidates.sort(
        key=lambda candidate: (
            -candidate.return_score,
            candidate.label,
            candidate.current_fragment_ids,
            candidate.past_fragment_ids,
        )
    )
    return candidates
