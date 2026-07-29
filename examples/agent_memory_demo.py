from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from so_memory import MemoryFragment, MemoryKernel, MemoryRelation


kernel = MemoryKernel()

result = kernel.run(
    [
        MemoryFragment(
            id="past_failed_action",
            content="agent_trace: action failure connected tool permission with missing approval",
            labels=["tool_permission", "missing_approval"],
            relations=[
                MemoryRelation(
                    "tool_permission",
                    "missing_approval",
                    relation_type="bridge",
                    strength=0.9,
                    directed=False,
                )
            ],
            memory_type="agent_trace",
            importance=0.9,
            persistence=0.8,
            novelty=0.7,
            bridge_potential=0.9,
        ),
        MemoryFragment(
            id="past_retry_blocker",
            content="agent_trace: retry connected tool permission with missing approval again",
            labels=["tool_permission", "missing_approval"],
            relations=[
                MemoryRelation(
                    "tool_permission",
                    "missing_approval",
                    relation_type="bridge",
                    strength=0.85,
                    directed=False,
                )
            ],
            memory_type="agent_trace",
            importance=0.85,
            persistence=0.8,
            novelty=0.65,
            bridge_potential=0.85,
        ),
        MemoryFragment(
            id="current_action",
            content="agent_trace: current action re-touches tool permission and missing approval",
            labels=["tool_permission", "missing_approval"],
            relations=[
                MemoryRelation(
                    "tool_permission",
                    "missing_approval",
                    relation_type="bridge",
                    strength=0.8,
                    directed=False,
                )
            ],
            memory_type="agent_trace",
            importance=0.8,
            persistence=0.8,
            novelty=0.6,
            bridge_potential=0.8,
            metadata={"phase": "current"},
        ),
    ]
)

print("Agent Memory Demo")
print("Pattern identity groups:", len(result.pattern_identity_groups))
for group in result.pattern_identity_groups:
    print(
        "  group:",
        group.pattern_type,
        "occurrences=",
        group.occurrence_count,
        "sources=",
        group.source_fragment_ids,
    )
print("Return candidates:", len(result.return_candidates))
for candidate in result.return_candidates:
    print("  return:", candidate.label)
    print("    current:", candidate.current_fragment_ids)
    print("    past:", candidate.past_fragment_ids)
    print("    reason:", candidate.connection_reason)
