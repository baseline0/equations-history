"""Pytest configuration and shared fixtures."""

import pytest


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
