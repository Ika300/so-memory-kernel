from __future__ import annotations

from .models import MemoryInput, MemoryKernelValidationError


def validate_memory_input(memory_input: MemoryInput) -> None:
    """Validate Memory Kernel input without applying semantic interpretation."""

    MemoryInput(memory_input.fragments)


__all__ = ["MemoryKernelValidationError", "validate_memory_input"]
