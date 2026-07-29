from __future__ import annotations

import sys
from pathlib import Path

from .adapter import memory_input_to_structured_json
from .evidence import evidence_identity_from_insight
from .models import MemoryFragment, MemoryInput, MemoryKernelResult
from .pattern_identity import pattern_identities_from_patterns
from .reactivation import return_candidates_from_pattern_groups


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CORE_PATH = _PROJECT_ROOT / "spiral_orbit_core"
if str(_CORE_PATH) not in sys.path:
    sys.path.insert(0, str(_CORE_PATH))

from spiral_orbit_attractor import generate_attractor_clusters  # noqa: E402
from spiral_orbit_boundary import generate_boundaries  # noqa: E402
from spiral_orbit_curiosity import generate_curiosities  # noqa: E402
from spiral_orbit_exploration import generate_exploration_targets  # noqa: E402
from spiral_orbit_insight import generate_insight_json  # noqa: E402
from spiral_orbit_microtopology import build_microtopologies  # noqa: E402
from spiral_orbit_overlay import generate_overlays  # noqa: E402
from spiral_orbit_pattern import generate_patterns  # noqa: E402


class MemoryKernel:
    """Thin SDK wrapper around the copied Spiral Orbit Core.

    This class does not modify SO formulas, thresholds, Pattern types, or pipeline
    architecture. Its job is to convert structural memory input into the Core's
    Structured JSON format and return the Core output with trace maps.
    """

    def run(self, fragments: list[MemoryFragment] | MemoryInput) -> MemoryKernelResult:
        memory_input = fragments if isinstance(fragments, MemoryInput) else MemoryInput(fragments)
        structured, fragment_to_sentence = memory_input_to_structured_json(memory_input)
        sentence_to_fragment = {sentence: fragment for fragment, sentence in fragment_to_sentence.items()}

        borderline_logs: list[str] = []
        microtopologies = build_microtopologies(structured)
        overlays = generate_overlays(microtopologies)
        patterns = generate_patterns(overlays, borderline_logs)
        clusters = generate_attractor_clusters(patterns, borderline_logs)
        boundaries = generate_boundaries(clusters, borderline_logs)
        curiosities = generate_curiosities(boundaries, borderline_logs)
        targets = generate_exploration_targets(curiosities, borderline_logs)
        insight = generate_insight_json(targets)

        evidence_identity = evidence_identity_from_insight(insight, sentence_to_fragment)
        pattern_identities, pattern_identity_groups = pattern_identities_from_patterns(
            patterns,
            sentence_to_fragment,
        )
        return_candidates = return_candidates_from_pattern_groups(
            pattern_identity_groups,
            memory_input.fragments,
        )
        return MemoryKernelResult(
            insight=insight,
            structured_json=structured,
            fragment_id_to_sentence_id=fragment_to_sentence,
            sentence_id_to_fragment_id=sentence_to_fragment,
            evidence_identity=evidence_identity,
            pattern_identities=pattern_identities,
            pattern_identity_groups=pattern_identity_groups,
            return_candidates=return_candidates,
        )
