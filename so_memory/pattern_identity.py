from __future__ import annotations

from .models import PatternIdentity, PatternIdentityGroup


def _preserve_first_seen(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _edge_signature(edge: object) -> str:
    source = getattr(edge, "source")
    target = getattr(edge, "target")
    relation_type = getattr(edge, "relation_type")
    directed = getattr(edge, "directed")
    if directed:
        endpoint = f"{source}->{target}"
    else:
        endpoint = "<->".join(sorted([source, target]))
    return f"{relation_type}:{endpoint}"


def pattern_identity_key(pattern: object) -> str:
    """Build an exact structural signature for a Core Pattern.

    This is intentionally not fuzzy. It does not merge by semantic similarity.
    A structure is treated as the same only when its type, center, members, and
    edge signatures match exactly after the Core's own normalization.
    """

    pattern_type = getattr(pattern, "pattern_type")
    center = getattr(pattern, "center_candidate")
    member_nodes = ",".join(getattr(pattern, "member_nodes"))
    edge_signatures = ",".join(
        sorted({_edge_signature(edge) for edge in getattr(pattern, "member_edges")})
    )
    return f"{pattern_type}|center={center}|members={member_nodes}|edges={edge_signatures}"


def pattern_identities_from_patterns(
    patterns: list[object],
    sentence_id_to_fragment_id: dict[str, str],
) -> tuple[list[PatternIdentity], list[PatternIdentityGroup]]:
    identities: list[PatternIdentity] = []
    for pattern in patterns:
        source_chain = getattr(pattern, "source_chain")
        sentence_ids = list(getattr(source_chain, "independent_source_sentence_ids", []))
        overlay_ids = list(getattr(source_chain, "contextual_recurrence_overlay_ids", []))
        fragment_ids = _preserve_first_seen(
            [
                sentence_id_to_fragment_id[sentence_id]
                for sentence_id in sentence_ids
                if sentence_id in sentence_id_to_fragment_id
            ]
        )
        identities.append(
            PatternIdentity(
                identity_key=pattern_identity_key(pattern),
                pattern_id=getattr(pattern, "id"),
                pattern_type=getattr(pattern, "pattern_type"),
                center_candidate=getattr(pattern, "center_candidate"),
                member_nodes=list(getattr(pattern, "member_nodes")),
                source_fragment_ids=fragment_ids,
                source_sentence_ids=sentence_ids,
                source_overlay_ids=list(getattr(pattern, "source_overlay_ids")),
                contextual_recurrence_overlay_ids=overlay_ids,
            )
        )

    groups_by_key: dict[str, list[PatternIdentity]] = {}
    for identity in identities:
        groups_by_key.setdefault(identity.identity_key, []).append(identity)

    groups: list[PatternIdentityGroup] = []
    for identity_key, group_identities in groups_by_key.items():
        first = group_identities[0]
        groups.append(
            PatternIdentityGroup(
                identity_key=identity_key,
                pattern_type=first.pattern_type,
                pattern_ids=[identity.pattern_id for identity in group_identities],
                center_candidate=first.center_candidate,
                member_nodes=list(first.member_nodes),
                source_fragment_ids=_preserve_first_seen(
                    [fragment_id for identity in group_identities for fragment_id in identity.source_fragment_ids]
                ),
                source_sentence_ids=_preserve_first_seen(
                    [sentence_id for identity in group_identities for sentence_id in identity.source_sentence_ids]
                ),
                contextual_recurrence_overlay_ids=_preserve_first_seen(
                    [overlay_id for identity in group_identities for overlay_id in identity.contextual_recurrence_overlay_ids]
                ),
            )
        )
    return identities, groups
