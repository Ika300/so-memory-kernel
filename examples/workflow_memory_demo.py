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
            id="past_api_blocker",
            content="workflow_event: backend task connected blocked export with schema migration",
            labels=["blocked_export", "schema_migration"],
            relations=[
                MemoryRelation(
                    "blocked_export",
                    "schema_migration",
                    relation_type="bridge",
                    strength=0.9,
                    directed=False,
                )
            ],
            memory_type="workflow_event",
            importance=0.9,
            persistence=0.85,
            novelty=0.65,
            bridge_potential=0.9,
        ),
        MemoryFragment(
            id="past_ui_blocker",
            content="workflow_event: UI integration repeated blocked export and schema migration",
            labels=["blocked_export", "schema_migration"],
            relations=[
                MemoryRelation(
                    "blocked_export",
                    "schema_migration",
                    relation_type="bridge",
                    strength=0.85,
                    directed=False,
                )
            ],
            memory_type="workflow_event",
            importance=0.85,
            persistence=0.8,
            novelty=0.65,
            bridge_potential=0.85,
        ),
        MemoryFragment(
            id="current_report_blocker",
            content="workflow_event: report export again connects blocked export with schema migration",
            labels=["blocked_export", "schema_migration"],
            relations=[
                MemoryRelation(
                    "blocked_export",
                    "schema_migration",
                    relation_type="bridge",
                    strength=0.8,
                    directed=False,
                )
            ],
            memory_type="workflow_event",
            importance=0.8,
            persistence=0.8,
            novelty=0.6,
            bridge_potential=0.8,
            metadata={"phase": "current"},
        ),
    ]
)

print("Workflow Memory Demo")
print("Evidence independent source count:", result.evidence_identity.independent_source_count)
print("Pattern identity groups:", len(result.pattern_identity_groups))
for group in result.pattern_identity_groups:
    print(
        "  group:",
        group.pattern_type,
        "center=",
        group.center_candidate,
        "sources=",
        group.source_fragment_ids,
    )
print("Return candidates:", len(result.return_candidates))
for candidate in result.return_candidates:
    print("  return:", candidate.label, candidate.shared_nodes)
