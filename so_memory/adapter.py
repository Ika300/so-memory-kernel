from __future__ import annotations

from typing import Any

from .models import MemoryFragment, MemoryInput


def _sentence_id(index: int) -> str:
    return f"s{index:03d}"


def _node_for_label(fragment: MemoryFragment, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "node_type": fragment.node_type,
        "importance": fragment.importance,
        "persistence": fragment.persistence,
        "valence": fragment.valence,
        "arousal": fragment.arousal,
        "certainty": fragment.certainty,
        "novelty": fragment.novelty,
        "abstraction": fragment.abstraction,
    }


def fragment_to_structured_json(fragment: MemoryFragment, sentence_id: str) -> dict[str, Any]:
    labels = fragment.structural_labels
    edges = [
        {
            "source": relation.source,
            "target": relation.target,
            "relation_type": relation.relation_type,
            "strength": relation.strength,
            "directed": relation.directed,
        }
        for relation in fragment.relations
    ]

    relation_labels: list[str] = []
    for relation in fragment.relations:
        for label in (relation.source, relation.target):
            if label not in labels and label not in relation_labels:
                relation_labels.append(label)

    all_labels = [*labels, *relation_labels]

    return {
        "sentence_id": sentence_id,
        "raw_text": fragment.content,
        "nodes": [_node_for_label(fragment, label) for label in all_labels],
        "edges": edges,
        "scores": {
            "importance": fragment.importance,
            "persistence": fragment.persistence,
            "valence": fragment.valence,
            "arousal": fragment.arousal,
            "certainty": fragment.certainty,
            "novelty": fragment.novelty,
            "bridge_potential": fragment.bridge_potential,
            "tension_score": fragment.tension_score,
            "gap_score": fragment.gap_score,
        },
        "categories": [fragment.memory_type, fragment.space_id],
        "notes": [
            f"memory_fragment_id={fragment.id}",
            f"memory_space_id={fragment.space_id}",
            f"memory_source_id={fragment.source_id or ''}",
            f"memory_created_at={fragment.created_at}",
        ],
    }


def memory_input_to_structured_json(memory_input: MemoryInput) -> tuple[list[dict[str, Any]], dict[str, str]]:
    fragment_to_sentence: dict[str, str] = {}
    structured: list[dict[str, Any]] = []
    for index, fragment in enumerate(memory_input.fragments, start=1):
        sentence_id = _sentence_id(index)
        fragment_to_sentence[fragment.id] = sentence_id
        structured.append(fragment_to_structured_json(fragment, sentence_id))
    return structured, fragment_to_sentence
