"""Shared assertion: an equation's computed source points at its Equation( call."""

import importlib
import linecache
from pathlib import Path

from equations_history.core import Equation


def assert_source_is_equation_call(eq: Equation) -> None:
    """Assert eq.source names a real line in the equation's own module that calls Equation(.

    The module is derived from the stable id ("<module>.<name>"), so the check
    does not depend on hand-typed line numbers.
    """
    module_name = eq.id.split(".", 1)[0]
    module = importlib.import_module(f"equations_history.equations.{module_name}")
    filename, lineno = eq.source
    assert Path(filename) == Path(module.__file__), f"{eq.id} source is in {filename}"
    assert lineno > 0, f"{eq.id} has no line number"
    line = linecache.getline(filename, lineno)
    assert line, f"{eq.id} source line {lineno} does not exist in {filename}"
    assert "Equation(" in line, f"{eq.id} source line {lineno} is {line.strip()!r}"
