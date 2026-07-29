from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from so_memory import MemoryFragment, MemoryKernel, MemoryRelation


kernel = MemoryKernel()

result = kernel.run([
    MemoryFragment(
        id="source_1",
        content="Source one supplies the memory structure bridge.",
        labels=["memory", "structure"],
        relations=[MemoryRelation("memory", "structure", relation_type="bridge", strength=0.9, directed=False)],
        importance=0.9,
        persistence=0.8,
        novelty=0.8,
        bridge_potential=0.9,
    ),
    MemoryFragment(
        id="source_2",
        content="Source two independently supplies the same memory structure bridge.",
        labels=["memory", "structure"],
        relations=[MemoryRelation("memory", "structure", relation_type="bridge", strength=0.85, directed=False)],
        importance=0.85,
        persistence=0.8,
        novelty=0.75,
        bridge_potential=0.85,
    ),
    MemoryFragment(
        id="source_3",
        content="The current source reactivates the same memory structure bridge.",
        labels=["memory", "structure"],
        relations=[MemoryRelation("memory", "structure", relation_type="bridge", strength=0.8, directed=False)],
        importance=0.8,
        persistence=0.8,
        novelty=0.7,
        bridge_potential=0.8,
        metadata={"phase": "current"},
    ),
])

print("Insight created:", result.has_insight)
print("Fragment to SO sentence ids:", result.fragment_id_to_sentence_id)
print("Structured JSON objects:", len(result.structured_json))
print("Independent source fragments:", result.evidence_identity.independent_source_fragment_ids)
print("Independent source count:", result.evidence_identity.independent_source_count)
print("Contextual recurrence count:", result.evidence_identity.contextual_recurrence_count)
print("Pattern identity groups:", len(result.pattern_identity_groups))
for group in result.pattern_identity_groups:
    print(
        "Pattern group:",
        group.pattern_type,
        "occurrences=",
        group.occurrence_count,
        "sources=",
        group.independent_source_count,
    )
print("Return candidates:", len(result.return_candidates))
for candidate in result.return_candidates:
    print(
        "Return:",
        candidate.label,
        "score=",
        candidate.return_score,
        "current=",
        candidate.current_fragment_ids,
        "past=",
        candidate.past_fragment_ids,
    )
