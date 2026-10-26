"""Ingest a formula catalog from math-trace into an equation topic.

math-trace writes one equations.json per template. Each entry is a formula with its LaTeX, its description, the line in
the template's model.py where its Formula(...) call starts, and its assumptions and units. This module reads a snapshot
of that file, checks it at the boundary, and joins it with the narrative equations-history owns: the display name, the
history, the citations and the concepts. Nothing here imports math-trace. The snapshot and its manifest are the only
interface, so a change in math-trace reaches this repo as a snapshot update, not as silent drift.

The contract is contracts/formula_catalog.schema.json. The checks below are the runtime form of that contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from equations_history import registry
from equations_history.core import Equation

CATALOG_FIELDS = frozenset({"latex", "description", "source_line", "assumptions", "units"})
NARRATIVE_FIELDS = frozenset({"name", "history", "citations", "concepts", "year"})


class CatalogError(ValueError):
    """A catalog or narrative file does not match its contract. The message names the file and the formula."""


@dataclass(frozen=True)
class CatalogEntry:
    """One formula as math-trace records it."""

    name: str
    latex: str
    description: str
    source_line: int
    assumptions: str
    units: str


@dataclass(frozen=True)
class Narrative:
    """The narrative equations-history owns for one formula."""

    name: str
    history: str
    citations: tuple[str, ...]
    concepts: tuple[str, ...]
    year: int | None


def _read_object(path: Path) -> dict[str, Any]:
    """The top-level JSON object of ``path``. It must be an object with at least one key."""
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"{path.name}: cannot read JSON: {error}") from error
    if not isinstance(data, dict) or not data:
        raise CatalogError(f"{path.name}: expected an object with at least one formula")
    return data


def _check_fields(path: Path, key: str, entry: Any, fields: frozenset[str]) -> dict[str, Any]:
    """``entry`` must be an object with exactly ``fields``. Returns it, typed for the caller."""
    if not isinstance(entry, dict):
        raise CatalogError(f"{path.name}: {key} must be an object")
    missing = fields - entry.keys()
    unexpected = entry.keys() - fields
    if missing or unexpected:
        raise CatalogError(
            f"{path.name}: {key} has missing {sorted(missing)} and unexpected {sorted(unexpected)} fields"
        )
    return entry


def _text(path: Path, key: str, field: str, value: Any, *, required: bool) -> str:
    """A string field. Required fields must not be blank."""
    if not isinstance(value, str) or (required and not value.strip()):
        raise CatalogError(f"{path.name}: {key}.{field} must be {'a non-empty ' if required else 'a '}string")
    return value


def _strings(path: Path, key: str, field: str, value: Any) -> tuple[str, ...]:
    """A non-empty list of non-blank strings."""
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise CatalogError(f"{path.name}: {key}.{field} must be a non-empty list of non-empty strings")
    return tuple(value)


def load_catalog(path: Path) -> dict[str, CatalogEntry]:
    """Formulas from a math-trace equations.json snapshot, checked against the catalog contract."""
    entries: dict[str, CatalogEntry] = {}
    for key, raw in _read_object(path).items():
        entry = _check_fields(path, key, raw, CATALOG_FIELDS)
        source_line = entry["source_line"]
        if not isinstance(source_line, int) or isinstance(source_line, bool) or source_line < 1:
            raise CatalogError(f"{path.name}: {key}.source_line must be a positive integer")
        entries[key] = CatalogEntry(
            name=key,
            latex=_text(path, key, "latex", entry["latex"], required=True),
            description=_text(path, key, "description", entry["description"], required=True),
            source_line=source_line,
            assumptions=_text(path, key, "assumptions", entry["assumptions"], required=False),
            units=_text(path, key, "units", entry["units"], required=False),
        )
    return entries


def load_narratives(path: Path) -> dict[str, Narrative]:
    """Narratives keyed by formula name. Each needs a display name, history, citations and concepts, and a year.

    The year is an integer, or null while it is not yet known. A null is a placeholder, not a missing field.
    """
    narratives: dict[str, Narrative] = {}
    for key, raw in _read_object(path).items():
        entry = _check_fields(path, key, raw, NARRATIVE_FIELDS)
        narratives[key] = Narrative(
            name=_text(path, key, "name", entry["name"], required=True),
            history=_text(path, key, "history", entry["history"], required=True),
            citations=_strings(path, key, "citations", entry["citations"]),
            concepts=_strings(path, key, "concepts", entry["concepts"]),
            year=_year(path, key, entry["year"]),
        )
    return narratives


def _year(path: Path, key: str, value: Any) -> int | None:
    """An introduction year, or None while it is unknown. A boolean or a non-integer is refused."""
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise CatalogError(f"{path.name}: {key}.year must be an integer year or null")
    return value


def _factory(topic: str, entry: CatalogEntry, narrative: Narrative, source_file: str) -> Callable[[], Equation]:
    """A factory that builds the Equation for one formula. Its source is the math-trace line, not this file's."""

    def build() -> Equation:
        equation = Equation(
            id=f"{topic}.{entry.name}",
            name=narrative.name,
            latex=entry.latex,
            description=entry.description,
            history=narrative.history,
            citations=list(narrative.citations),
            concepts=list(narrative.concepts),
            year=narrative.year,
        )
        equation.source = (source_file, entry.source_line)
        return equation

    return build


def register_catalog_topic(
    topic: str,
    module: str,
    catalog_path: Path,
    narrative_path: Path,
    source_file: str,
) -> None:
    """Register every formula in ``catalog_path`` under ``topic``, with its narrative from ``narrative_path``.

    ``module`` is the topic module's dotted name, so each factory reports where it was registered. ``source_file`` is
    the template's model.py in math-trace, which is where each recorded source_line points. The two files must name
    the same formulas: a formula with no narrative, or a narrative with no formula, fails here.
    """
    entries = load_catalog(catalog_path)
    narratives = load_narratives(narrative_path)
    if entries.keys() != narratives.keys():
        without_narrative = sorted(entries.keys() - narratives.keys())
        without_formula = sorted(narratives.keys() - entries.keys())
        raise CatalogError(
            f"{topic}: formulas without a narrative {without_narrative}; narratives without a formula {without_formula}"
        )
    for name, entry in entries.items():
        factory = _factory(topic, entry, narratives[name], source_file)
        factory.__name__ = name
        factory.__qualname__ = name
        factory.__module__ = module
        registry.register(topic, name, factory)
