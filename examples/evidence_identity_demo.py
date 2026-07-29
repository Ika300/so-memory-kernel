from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from so_memory import MemoryFragment, MemoryKernel, MemoryRelation


def bridge_fragment(fragment_id: str, content: str) -> MemoryFragment:
    return MemoryFragment(
        id=fragment_id,
        content=content,
        labels=["art", "religion"],
        relations=[
            MemoryRelation(
                "art",
                "religion",
                relation_type="bridge",
                strength=0.85,
                directed=False,
            )
        ],
        importance=0.85,
        novelty=0.75,
        bridge_potential=0.85,
    )


kernel = MemoryKernel()

one_source_many_contexts = kernel.run(
    [
        bridge_fragment("bridge_source", "One source supplies the bridge."),
        MemoryFragment(id="context_1", content="Weather context.", labels=["weather"]),
        MemoryFragment(id="context_2", content="Food context.", labels=["food"]),
        MemoryFragment(id="context_3", content="Traffic context.", labels=["traffic"]),
    ]
)

many_independent_sources = kernel.run(
    [
        bridge_fragment("source_1", "Independent source one supplies the bridge."),
        bridge_fragment("source_2", "Independent source two supplies the bridge."),
        bridge_fragment("source_3", "Independent source three supplies the bridge."),
    ]
)

print("Condition A: one source, many contexts")
print("  independent source fragments:", one_source_many_contexts.evidence_identity.independent_source_fragment_ids)
print("  independent source count:", one_source_many_contexts.evidence_identity.independent_source_count)
print("  contextual recurrence count:", one_source_many_contexts.evidence_identity.contextual_recurrence_count)

print("Condition B: many independent sources")
print("  independent source fragments:", many_independent_sources.evidence_identity.independent_source_fragment_ids)
print("  independent source count:", many_independent_sources.evidence_identity.independent_source_count)
print("  contextual recurrence count:", many_independent_sources.evidence_identity.contextual_recurrence_count)
