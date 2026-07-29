from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from spiral_orbit_attractor import generate_attractor_clusters
from spiral_orbit_boundary import generate_boundaries
from spiral_orbit_curiosity import generate_curiosities
from spiral_orbit_exploration import generate_exploration_targets
from spiral_orbit_insight import generate_insight_json
from spiral_orbit_microtopology import build_microtopologies
from spiral_orbit_models import InsightJSON
from spiral_orbit_overlay import generate_overlays
from spiral_orbit_pattern import generate_patterns


def run_pipeline(
    structured_json_objects: list[Mapping[str, Any]],
    project_root: Path | None = None,
) -> InsightJSON | None:
    borderline_logs: list[str] = []
    microtopologies = build_microtopologies(structured_json_objects)
    overlays = generate_overlays(microtopologies)
    patterns = generate_patterns(overlays, borderline_logs)
    clusters = generate_attractor_clusters(patterns, borderline_logs)
    boundaries = generate_boundaries(clusters, borderline_logs)
    curiosities = generate_curiosities(boundaries, borderline_logs)
    targets = generate_exploration_targets(curiosities, borderline_logs)
    insight = generate_insight_json(targets)

    if project_root is not None:
        log_path = project_root / "logs" / "Spiral_Orbit_Borderline.log"
        log_path.write_text(
            "\n".join(borderline_logs) + ("\n" if borderline_logs else ""),
            encoding="utf-8",
        )
    return insight
