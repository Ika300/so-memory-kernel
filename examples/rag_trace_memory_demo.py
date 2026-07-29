from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from so_memory import MemoryFragment, MemoryKernel, MemoryRelation


def retrieved_claim(fragment_id: str, source_id: str, current: bool = False) -> MemoryFragment:
    return MemoryFragment(
        id=fragment_id,
        content=f"rag_trace: {source_id} supports claim via policy evidence",
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


kernel = MemoryKernel()

result = kernel.run(
    [
        retrieved_claim("chunk_a", "document_a"),
        retrieved_claim("chunk_b", "document_b"),
        retrieved_claim("chunk_c_repeat", "document_a"),
        retrieved_claim("current_chunk", "document_c", current=True),
    ]
)

print("RAG Trace Memory Demo")
print("Independent source fragments:", result.evidence_identity.independent_source_fragment_ids)
print("Independent source count:", result.evidence_identity.independent_source_count)
print("Contextual recurrence count:", result.evidence_identity.contextual_recurrence_count)
print("Pattern identity groups:", len(result.pattern_identity_groups))
for group in result.pattern_identity_groups:
    print(
        "  group:",
        group.pattern_type,
        "occurrences=",
        group.occurrence_count,
        "source_fragments=",
        group.source_fragment_ids,
    )
print("Return candidates:", len(result.return_candidates))
for candidate in result.return_candidates:
    print("  return:", candidate.label, "current=", candidate.current_fragment_ids, "past=", candidate.past_fragment_ids)
