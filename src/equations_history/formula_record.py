"""Formula records (formula-record/1): validation, unit consistency, the public view, and the literature licence rule.

Everything here is pure: it takes parsed JSON and returns values or error messages. Reading files and printing belong to
the CLI. The schema in contracts/formula_record.schema.json is the contract; ``validate_record`` is its runtime form.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import cache
from typing import Any

import jsonschema
import pint

from equations_history.constants import FORMULA_RECORD_SCHEMA_PATH
from equations_history.formula_catalog import CatalogEntry, Narrative
from equations_history.paper_store import ALLOWED_LICENCES, PaperStore, PaperStoreError

# The fields a record may show on the public site. Anything not named here is dropped by ``public_view``. Internal file
# paths and source lines are withheld; add them here only as a deliberate decision.
PUBLIC_FIELDS: Mapping[str, Any] = {
    "id": None,
    "core": {"name", "latex", "units", "assumptions"},
    "provenance": {
        "code": {"repo"},
        "literature": {"paper_store_id", "version", "locator"},
    },
    "narrative": {"year", "history", "citations", "concepts"},
}

_ureg = pint.UnitRegistry()


@cache
def _validator() -> jsonschema.Draft202012Validator:
    """The validator for the formula-record/1 contract, built once."""
    schema = json.loads(FORMULA_RECORD_SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


def validate_record(record: Mapping[str, Any]) -> list[str]:
    """Every contract violation in ``record``, as messages with their JSON paths. An empty list means it is valid."""
    errors = sorted(_validator().iter_errors(record), key=lambda error: list(error.absolute_path))
    return [f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in errors]


def units_agree(lhs: str, rhs: str) -> bool:
    """True when the two unit expressions have the same dimensions, for example kg/(m s^2) and N/m^2.

    An expression pint cannot parse raises ``pint.errors.PintError``; the caller decides how to report it.
    """
    return _ureg.parse_expression(lhs).dimensionality == _ureg.parse_expression(rhs).dimensionality


def unit_problems(units: Mapping[str, str]) -> list[str]:
    """Why ``units`` cannot describe one equation: unparseable units, or a dimension mismatch. Empty when consistent."""
    try:
        if units_agree(units["lhs"], units["rhs"]):
            return []
    except pint.errors.PintError as error:
        return [f"units cannot be parsed: {error}"]
    return [f"dimension mismatch: lhs {units['lhs']!r} and rhs {units['rhs']!r} differ"]


def literature_is_open(licence: str | None) -> bool:
    """True only for an exact canonical open licence from the paper-store contract. A missing licence is not open."""
    return licence in ALLOWED_LICENCES


def public_view(record: Mapping[str, Any]) -> dict[str, Any]:
    """The record reduced to ``PUBLIC_FIELDS``. Optional blocks absent from the record stay absent."""
    return _pick(record, PUBLIC_FIELDS)


def _pick(value: Mapping[str, Any], allowed: Any) -> dict[str, Any]:
    """Keep only the keys named by ``allowed``, recursing where it nests. A ``None`` leaf keeps the value whole."""
    kept: dict[str, Any] = {}
    for key, sub in allowed.items():
        if key not in value:
            continue
        if sub is None:
            kept[key] = value[key]
        elif isinstance(sub, Mapping):
            kept[key] = _pick(value[key], sub)
        else:
            kept[key] = {field: value[key][field] for field in sub if field in value[key]}
    return kept


def record_problems(record: Mapping[str, Any]) -> list[str]:
    """Every problem that stops ``record`` from being published: contract violations first, then unit consistency.

    Unit checks run only on a record that passes the contract, because they read fields the contract guarantees.
    """
    errors = validate_record(record)
    if errors:
        return errors
    return unit_problems(record["core"]["units"])


class AssemblyError(ValueError):
    """A formula cannot be joined into a valid record. The message names the record and the reason."""


def assemble_record(
    record_id: str,
    entry: CatalogEntry,
    narrative: Narrative,
    *,
    source_file: str,
    store: PaperStore,
    literature: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Join one math-trace catalog entry and its narrative into a formula-record/1 object, and check it.

    ``source_file`` is the template's model.py path in math-trace, which the catalog does not carry. ``literature`` is
    an optional ``paper_store_id``, ``version`` and ``locator``. The finished record goes through ``check_record``
    against ``store``, so a restricted or out-of-date paper is refused here rather than at publish time.
    """
    if not entry.units_lhs.strip() or not entry.units_rhs.strip():
        raise AssemblyError(f"{record_id}: math-trace has not declared units_lhs and units_rhs for this formula")
    record: dict[str, Any] = {
        "id": record_id,
        "core": {
            "name": narrative.name,
            "latex": entry.latex,
            "units": {"lhs": entry.units_lhs, "rhs": entry.units_rhs},
            "assumptions": [entry.assumptions] if entry.assumptions.strip() else [],
        },
        "provenance": {
            "code": {"repo": "math-trace", "file": source_file, "source_line": entry.source_line},
        },
        "narrative": {
            "year": narrative.year,
            "history": narrative.history,
            "citations": list(narrative.citations),
            "concepts": list(narrative.concepts),
        },
    }
    if literature is not None:
        record["provenance"]["literature"] = dict(literature)
    problems = check_record(record, store)
    if problems:
        raise AssemblyError(f"{record_id}: " + "; ".join(problems))
    return record


def literature_problems(record: Mapping[str, Any], store: PaperStore) -> list[str]:
    """What the paper store says about a record's literature block. Empty when there is none, or it is open and current.

    The store refuses a restricted licence itself. The licence is checked again here, as the paper-store contract asks
    every reader to do. The record must pin the store's latest version, so a newer paper cannot be quoted under an old pin.
    """
    literature = record.get("provenance", {}).get("literature")
    if literature is None:
        return []
    arxiv_id = literature["paper_store_id"]
    try:
        manifest = store.read_manifest(arxiv_id)
    except PaperStoreError as error:
        return [f"literature {arxiv_id}: {error}"]
    problems: list[str] = []
    if not literature_is_open(manifest.licence):
        problems.append(f"literature {arxiv_id}: licence {manifest.licence!r} is not open")
    if manifest.version != literature["version"]:
        problems.append(
            f"literature {arxiv_id}: record pins {literature['version']} but the store's latest is {manifest.version}"
        )
    return problems


def check_record(record: Mapping[str, Any], store: PaperStore) -> list[str]:
    """Everything that blocks publication: the record problems, then the paper-store check.

    The paper-store check runs only on a well-formed record, because it reads the literature block the contract checks.
    """
    problems = record_problems(record)
    if problems:
        return problems
    return literature_problems(record, store)
