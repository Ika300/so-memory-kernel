from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "benchmarks"))

from run_benchmarks import run


class BenchmarkRunnerTests(unittest.TestCase):
    def test_benchmark_runner_passes_all_cases(self) -> None:
        payload = run()
        self.assertEqual(payload["summary"]["failed"], 0)
        self.assertEqual(payload["summary"]["passed"], payload["summary"]["total"])
        self.assertGreaterEqual(payload["summary"]["total"], 7)


if __name__ == "__main__":
    unittest.main()
