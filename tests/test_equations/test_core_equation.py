"""Tests for the shared Equation record: frame-captured source and stable ids."""

import importlib
import inspect
import linecache
from dataclasses import fields
from pathlib import Path

import pytest

from equations_history.core import Equation
from test_equations.source_check import assert_source_is_equation_call

TOPIC_MODULES = ["autoencoders", "bert", "diffusion", "entropy", "loss_functions", "optimizers", "regularization"]


def _build_via_helper() -> Equation:
    """Construct an equation from a helper function; source should name this helper's call."""
    return Equation(
        id="test.helper",
        name="Helper",
        latex="x",
        description="d",
        history="h",
        citations=["c"],
        concepts=["k"],
    )


def test_source_records_the_equation_call_line() -> None:
    """source is (filename, lineno) of the Equation( call that built the record."""
    eq = Equation(  # this call starts on the recorded line
        id="test.direct",
        name="Direct",
        latex="x",
        description="d",
        history="h",
        citations=["c"],
        concepts=["k"],
    )
    filename, lineno = eq.source
    assert Path(filename) == Path(__file__)
    assert "Equation(" in linecache.getline(filename, lineno)


def test_source_skips_internal_frames_and_names_the_caller() -> None:
    """The recorded line is the caller's call site, not core.py or the generated __init__."""
    eq = _build_via_helper()
    source_lines, first_line = inspect.getsourcelines(_build_via_helper)
    call_line = first_line + next(i for i, text in enumerate(source_lines) if "Equation(" in text)
    assert eq.source == (eq.source[0], call_line)
    assert Path(eq.source[0]) == Path(__file__)


def test_source_is_not_an_init_argument() -> None:
    """source is computed, so it is absent from __init__ and cannot be passed."""
    init_names = {f.name for f in fields(Equation) if f.init}
    assert "source" not in init_names
    assert {"id", "name", "latex", "description", "history", "citations", "concepts"} == init_names
    with pytest.raises(TypeError):
        Equation(  # type: ignore[call-arg]
            id="test.bad",
            name="Bad",
            latex="x",
            description="d",
            history="h",
            citations=[],
            concepts=[],
            source=("nowhere.py", 1),
        )


def test_source_label_formats_basename_and_line() -> None:
    """source_label is the short "<file>.py:<line>" form used by the API and CLI."""
    eq = Equation(
        id="test.label",
        name="Label",
        latex="x",
        description="d",
        history="h",
        citations=[],
        concepts=[],
    )
    filename, lineno = eq.source
    assert eq.source_label == f"{Path(filename).name}:{lineno}"
    assert eq.source_label.startswith("test_core_equation.py:")


@pytest.mark.parametrize("module_name", TOPIC_MODULES)
def test_every_equation_in_module_resolves_to_its_call(module_name: str) -> None:
    """Each equation in a topic module points at an Equation( line in that module."""
    module = importlib.import_module(f"equations_history.equations.{module_name}")
    for eq in module.get_all_equations().values():
        assert_source_is_equation_call(eq)


def test_equation_ids_are_unique_across_the_package() -> None:
    """Every id is "<module>.<key>" and no id repeats across topic modules."""
    ids: list[str] = []
    for module_name in TOPIC_MODULES:
        module = importlib.import_module(f"equations_history.equations.{module_name}")
        for key, eq in module.get_all_equations().items():
            assert eq.id == f"{module_name}.{key}"
            ids.append(eq.id)
    assert len(ids) == len(set(ids))
