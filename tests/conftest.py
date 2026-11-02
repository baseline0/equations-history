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

# Why: each test file lives in the tier folder that names it, and the folder gives the tier marker. The fleet
# placement check reads this tuple to know which folders are tiers. Same convention as cv.
TESTS_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
TIER_MARKERS = ("unit", "integration", "contract", "host", "e2e")


def pytest_configure(config: pytest.Config) -> None:
    for tier in TIER_MARKERS:
        config.addinivalue_line("markers", f"{tier}: tests in tests/{tier}/")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Add the marker of each test's tier folder, and refuse a test outside a tier folder."""
    for item in items:
        relative = Path(str(item.path)).relative_to(TESTS_ROOT)
        tier = relative.parts[0] if len(relative.parts) > 1 else ""
        if tier not in TIER_MARKERS:
            raise pytest.UsageError(f"{item.nodeid}: move this test into one of tests/{{{','.join(TIER_MARKERS)}}}/")
        for other in TIER_MARKERS:
            if other != tier and item.get_closest_marker(other):
                raise pytest.UsageError(
                    f"{item.nodeid}: do not declare @pytest.mark.{other}; this test is in {tier}/ "
                    f"and gets @pytest.mark.{tier} from its folder."
                )
        item.add_marker(getattr(pytest.mark, tier))


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
