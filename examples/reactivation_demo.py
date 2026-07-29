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
            id="past_design",
            content="Past memory: structure and meaning were connected in a design note.",
            labels=["structure", "meaning"],
            relations=[
                MemoryRelation(
                    "structure",
                    "meaning",
                    relation_type="bridge",
                    strength=0.9,
                    directed=False,
                )
            ],
            importance=0.9,
            novelty=0.8,
            bridge_potential=0.9,
        ),
        MemoryFragment(
            id="current_design",
            content="Current memory: structure and meaning become connected again.",
            labels=["structure", "meaning"],
            relations=[
                MemoryRelation(
                    "structure",
                    "meaning",
                    relation_type="bridge",
                    strength=0.85,
                    directed=False,
                )
            ],
            importance=0.85,
            novelty=0.75,
            bridge_potential=0.85,
            metadata={"phase": "current"},
        ),
    ]
)

print("Return candidates:", len(result.return_candidates))
for candidate in result.return_candidates:
    print("label:", candidate.label)
    print("score:", candidate.return_score)
    print("current fragments:", candidate.current_fragment_ids)
    print("past fragments:", candidate.past_fragment_ids)
    print("shared nodes:", candidate.shared_nodes)
    print("caution:", candidate.caution)
