"""Tests for the @equation decorator registry."""

import importlib
import pkgutil
import re

import pytest

from equations_history import equations as equations_pkg
from equations_history import registry
from equations_history.core import Equation
from equations_history.registry import equation, equations_for, get, names, topics


@pytest.fixture
def isolated_registry(monkeypatch: pytest.MonkeyPatch) -> dict[str, dict[str, registry.EquationFactory]]:
    """Give a test an empty registry so its decorators do not leak into the package registry."""
    fresh: dict[str, dict[str, registry.EquationFactory]] = {}
    monkeypatch.setattr(registry, "_registry", fresh)
    return fresh


def _topic_module_names() -> list[str]:
    """Every module in the equations package, discovered from disk rather than a hand list."""
    return sorted(info.name for info in pkgutil.iter_modules(equations_pkg.__path__))


def test_decorated_method_is_found_by_topic_and_name(
    isolated_registry: dict[str, dict[str, registry.EquationFactory]],
) -> None:
    class Demo:
        @staticmethod
        @equation("demo")
        def first() -> Equation:
            return Equation(
                id="demo.first", name="First", latex="", description="", history="", citations=[], concepts=[]
            )

    assert topics() == ["demo"]
    assert names("demo") == ["first"]
    assert get("demo", "first").id == "demo.first"
    assert Demo.first().id == "demo.first"


def test_decorator_returns_the_function_unchanged(
    isolated_registry: dict[str, dict[str, registry.EquationFactory]],
) -> None:
    def factory() -> Equation:
        return Equation(id="t.factory", name="F", latex="", description="", history="", citations=[], concepts=[])

    assert equation("t")(factory) is factory


def test_duplicate_topic_and_name_raises(isolated_registry: dict[str, dict[str, registry.EquationFactory]]) -> None:
    @equation("dup")
    def same() -> Equation:
        return Equation(id="dup.same", name="S", latex="", description="", history="", citations=[], concepts=[])

    with pytest.raises(ValueError, match=re.escape("Duplicate equation dup.same")):
        equation("dup")(same)


@pytest.mark.parametrize("module_name", _topic_module_names())
def test_every_topic_module_registers_at_least_one_equation(module_name: str) -> None:
    importlib.import_module(f"equations_history.equations.{module_name}")
    assert names(module_name), f"{module_name} registered no equations"


def test_registry_names_match_method_names() -> None:
    for topic in topics():
        for name in names(topic):
            found = get(topic, name)
            assert found.id == f"{topic}.{name}"
            factory = registry._registry[topic][name]
            assert factory.__name__ == name
            assert factory.__module__ == f"equations_history.equations.{topic}"
            assert factory.__qualname__.split(".")[-1] == name


def test_equations_for_matches_get_for_every_name() -> None:
    for topic in topics():
        by_topic = equations_for(topic)
        assert list(by_topic) == names(topic)
        for name, eq in by_topic.items():
            assert eq.id == get(topic, name).id
