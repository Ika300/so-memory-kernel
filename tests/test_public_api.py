from __future__ import annotations

import unittest


class PublicAPITests(unittest.TestCase):
    def test_public_imports_are_available(self) -> None:
        from so_memory import (
            EvidenceIdentity,
            MemoryFragment,
            MemoryInput,
            MemoryKernel,
            MemoryKernelResult,
            MemoryKernelValidationError,
            MemoryRelation,
            PatternIdentity,
            PatternIdentityGroup,
            ReturnCandidate,
        )

        self.assertIsNotNone(EvidenceIdentity)
        self.assertIsNotNone(MemoryFragment)
        self.assertIsNotNone(MemoryInput)
        self.assertIsNotNone(MemoryKernel)
        self.assertIsNotNone(MemoryKernelResult)
        self.assertIsNotNone(MemoryKernelValidationError)
        self.assertIsNotNone(MemoryRelation)
        self.assertIsNotNone(PatternIdentity)
        self.assertIsNotNone(PatternIdentityGroup)
        self.assertIsNotNone(ReturnCandidate)


if __name__ == "__main__":
    unittest.main()
