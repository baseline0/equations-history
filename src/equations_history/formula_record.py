"""Formula records (formula-record/1): validation, unit consistency, the public view, and the literature licence rule.

Everything here is pure: it takes parsed JSON and returns values or error messages. Reading files and printing belong to
the CLI. The schema in contracts/formula_record.schema.json is the contract; ``validate_record`` is its runtime form.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| A formula record is valid only when it satisfies `contracts/formula_record.schema.json` (Draft 2020-12) | `contracts/formula_record.schema.json` | `_validator`, `validate_record`; `tests/unit/test_formula_record.py::test_the_schema_is_valid_draft_2020_12`, `test_the_pilot_record_is_valid`, `test_every_fixture_record_is_valid`, `test_the_contract_rejects_malformed_records` |
| Literature block is optional; when present it must have canonical paper-store id/version/locator and no self-attested licence flag | `contracts/formula_record.schema.json`; paper-store contract | `validate_record`; `tests/unit/test_formula_record.py::test_a_literature_block_is_optional`, `test_the_contract_rejects_malformed_records` |
| Literature locator names a human-readable location and must not carry raw TeX/LaTeX markup | record publication contract | `validate_record` via schema; `tests/unit/test_formula_record.py::test_a_literature_locator_never_carries_raw_tex`, `test_a_plain_literature_locator_is_accepted_by_the_contract` |
| Unit consistency is checked only after schema validation passes; parse errors and dimension mismatches are reported, not raised | unit-consistency contract | `record_problems`, `unit_problems`, `units_agree`; `tests/unit/test_formula_record.py::test_units_with_the_same_dimensions_agree`, `test_units_with_different_dimensions_are_reported`, `test_units_pint_cannot_parse_are_reported_not_raised`, `test_a_record_that_fails_the_contract_is_not_unit_checked` |
| Only canonical open licences are accepted; missing/non-canonical/NC licences are refused | paper-store licence contract | `literature_is_open`, `literature_problems`; `tests/unit/test_formula_record.py::test_the_three_open_licences_are_accepted`, `test_any_other_licence_is_refused`, `test_a_literature_block_on_a_restricted_paper_is_refused` |
| Literature must pin the store's latest version; unknown/restricted/old-version papers are refused | paper-store contract | `literature_problems`, `check_record`; `tests/unit/test_formula_record.py::test_a_literature_block_on_an_open_current_paper_passes`, `test_a_literature_block_on_an_unknown_paper_is_refused`, `test_a_literature_block_pinning_an_old_version_is_refused`, `test_check_record_skips_the_paper_store_when_the_record_is_malformed` |
| Public view exposes only `PUBLIC_FIELDS`; internal provenance paths/source lines are withheld; input is not mutated | publication boundary contract | `PUBLIC_FIELDS`, `public_view`, `_pick`; `tests/unit/test_formula_record.py::test_the_public_view_drops_internal_provenance_and_keeps_the_narrative`, `test_the_public_view_keeps_a_literature_locator_but_no_tex`, `test_the_public_view_does_not_mutate_its_input` |
| Assembly requires declared `units_lhs` and `units_rhs`; assembled record must pass `check_record` before return | assembly contract | `assemble_record`; `tests/unit/test_formula_record.py::test_the_assembler_reproduces_the_michaelis_menten_record_from_its_sources`, `test_the_assembler_refuses_a_formula_whose_units_math_trace_has_not_declared`, `test_the_assembler_accepts_max_velocity_once_its_units_are_declared` |
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
    expr_hash: str | None = None,
    commit: str | None = None,
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
            "code": {
                "repo": "math-trace",
                "file": source_file,
                "source_line": entry.source_line,
                **({"expr_hash": expr_hash} if expr_hash else {}),
                **({"commit": commit} if commit else {}),
            },
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
