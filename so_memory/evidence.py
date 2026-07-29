from __future__ import annotations

from .models import EvidenceIdentity


def _map_sentences_to_fragments(
    sentence_ids: list[str], sentence_id_to_fragment_id: dict[str, str]
) -> list[str]:
    result: list[str] = []
    for sentence_id in sentence_ids:
        fragment_id = sentence_id_to_fragment_id.get(sentence_id)
        if fragment_id is not None and fragment_id not in result:
            result.append(fragment_id)
    return result


def evidence_identity_from_insight(
    insight: object | None,
    sentence_id_to_fragment_id: dict[str, str],
) -> EvidenceIdentity:
    """Extract evidence identity from the final SO Insight source chain.

    This reads evidence history already produced by the copied SO Core. It does
    not change Pattern counts, merge evidence, or invent semantic identity.
    """

    if insight is None:
        return EvidenceIdentity()

    source_chain = getattr(insight, "source_chain", None)
    if source_chain is None:
        return EvidenceIdentity()

    independent_sentence_ids = list(getattr(source_chain, "independent_source_sentence_ids", []))
    independent_microtopology_ids = list(getattr(source_chain, "independent_source_microtopology_ids", []))
    contextual_overlay_ids = list(getattr(source_chain, "contextual_recurrence_overlay_ids", []))

    return EvidenceIdentity(
        independent_source_sentence_ids=independent_sentence_ids,
        independent_source_fragment_ids=_map_sentences_to_fragments(
            independent_sentence_ids, sentence_id_to_fragment_id
        ),
        independent_source_microtopology_ids=independent_microtopology_ids,
        contextual_recurrence_overlay_ids=contextual_overlay_ids,
    )
