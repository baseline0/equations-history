"""Registry of equation methods, filled by the ``@equation`` decorator.

Each topic module decorates its static methods that return an Equation. The
registry is the one place that lists them, so the CLI and API are generated
from it instead of keeping their own lists in step.
"""

from collections.abc import Callable

from equations_history.core import Equation

EquationFactory = Callable[[], Equation]

_registry: dict[str, dict[str, EquationFactory]] = {}


def equation(topic: str) -> Callable[[EquationFactory], EquationFactory]:
    """Record a method under ``topic`` (keyed by its name) and return it unchanged."""

    def register(factory: EquationFactory) -> EquationFactory:
        methods = _registry.setdefault(topic, {})
        if factory.__name__ in methods:
            raise ValueError(f"Duplicate equation {topic}.{factory.__name__}")
        methods[factory.__name__] = factory
        return factory

    return register


def topics() -> list[str]:
    """Topic names in registration order."""
    return list(_registry)


def names(topic: str) -> list[str]:
    """Method names registered under ``topic``, in definition order."""
    return list(_registry[topic])


def equations_for(topic: str) -> dict[str, Equation]:
    """Call each factory registered under ``topic``; keyed by method name."""
    return {name: factory() for name, factory in _registry[topic].items()}


def get(topic: str, name: str) -> Equation:
    """Call the single factory registered as ``topic``/``name``."""
    return _registry[topic][name]()
