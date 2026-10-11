"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Why: a bare `python` or `pytest` on PATH can be another project's venv, and then the tests import the
# wrong packages or fail on imports. Refuse to run anywhere except the project venv, before any project import.
_PROJECT_VENV = (Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / ".venv").resolve()
if Path(sys.prefix).resolve() != _PROJECT_VENV:
    raise pytest.UsageError(
        f"tests must run in the project venv {_PROJECT_VENV}, but this interpreter is {sys.prefix}. "
        "Run them with: uv run pytest"
    )


@pytest.fixture
def sample_equation_metadata() -> dict:
    """Sample equation metadata for testing."""
    return {
        "name": "Test Equation",
        "latex": r"x = y + z",
        "description": "A test equation",
        "history": "This is a test",
        "citations": ["Test citation"],
        "source_line": 42,
        "concepts": ["test"],
    }
