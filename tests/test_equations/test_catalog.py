"""Tests for ingesting a math-trace formula catalog: the snapshot, the boundary checks, and the biochemistry topic."""

import hashlib
import json
import re
from collections.abc import Callable
from pathlib import Path

import jsonschema
import pytest
from typer.testing import CliRunner

from equations_history import registry
from equations_history.cli import app
from equations_history.constants import CATALOG_DIR, NARRATIVE_DIR, REPO_ROOT
from equations_history.equations import biochemistry
from equations_history.formula_catalog import (
    CatalogError,
    load_catalog,
    load_narratives,
    register_catalog_topic,
)

CATALOG = CATALOG_DIR / "biochemistry.json"
NARRATIVE = NARRATIVE_DIR / "biochemistry.json"
MANIFEST = CATALOG_DIR / "biochemistry.manifest.json"
SCHEMA = REPO_ROOT / "contracts" / "formula_catalog.schema.json"

FORMULA = {
    "latex": "v = \\frac{S V_{max}}{K_{m} + S}",
    "description": "Michaelis-Menten equation",
    "source_line": 32,
    "assumptions": "Quasi-steady-state",
    "units": "umol/min",
}
NARRATIVE_ENTRY = {
    "name": "Michaelis-Menten Equation",
    "history": "Derived in 1913.",
    "citations": ["Michaelis & Menten (1913)."],
    "concepts": ["enzyme kinetics"],
}


def _write(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def fresh_registry(monkeypatch: pytest.MonkeyPatch) -> dict[str, dict[str, registry.EquationFactory]]:
    """An empty registry for the test, so registrations do not leak into other tests."""
    empty: dict[str, dict[str, registry.EquationFactory]] = {}
    monkeypatch.setattr(registry, "_registry", empty)
    return empty


def test_snapshot_matches_its_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())

    assert hashlib.sha256(CATALOG.read_bytes()).hexdigest() == manifest["sha256"]


def test_snapshot_validates_against_the_contract_schema() -> None:
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)

    jsonschema.Draft202012Validator(schema).validate(json.loads(CATALOG.read_text()))


def test_biochemistry_topic_registers_the_six_catalog_formulas() -> None:
    assert registry.names("biochemistry") == [
        "michaelis_menten",
        "max_velocity",
        "michaelis_constant",
        "enzyme_mechanism",
        "turnover_number",
        "specificity",
    ]


def test_each_equation_takes_latex_from_the_catalog_and_source_from_math_trace() -> None:
    catalog = load_catalog(CATALOG)

    for name, eq in biochemistry.get_all_equations().items():
        entry = catalog[name]
        assert eq.id == f"biochemistry.{name}"
        assert eq.latex == entry.latex
        assert eq.description == entry.description
        assert eq.source == (biochemistry.MATH_TRACE_MODEL, entry.source_line)
        assert eq.citations and eq.concepts
        assert eq.source_label == f"model.py:{entry.source_line}"


def test_factories_report_the_topic_module_they_were_registered_from() -> None:
    for name in registry.names("biochemistry"):
        factory = registry._registry["biochemistry"][name]
        assert factory.__module__ == "equations_history.equations.biochemistry"
        assert factory.__name__ == name


def test_cli_lists_biochemistry_from_the_catalog() -> None:
    result = CliRunner().invoke(app, ["biochemistry", "--topic", "all", "--explain", "false", "--citations", "false"])

    assert result.exit_code == 0, result.output
    assert "Michaelis-Menten Equation" in result.output
    assert "specificity" in result.output


# Boundary checks. Each sample is rejected by the Python loader and by the contract schema.

BAD_CATALOGS: dict[str, Callable[[dict[str, object]], None]] = {
    "missing field": lambda f: f.pop("units"),
    "unexpected field": lambda f: f.update(verified=True),
    "zero source_line": lambda f: f.update(source_line=0),
    "string source_line": lambda f: f.update(source_line="32"),
    "boolean source_line": lambda f: f.update(source_line=True),
    "blank latex": lambda f: f.update(latex="  "),
}


@pytest.mark.parametrize("case", sorted(BAD_CATALOGS))
def test_bad_catalog_entries_are_rejected_by_loader_and_schema(case: str, tmp_path: Path) -> None:
    formula = {**FORMULA}
    BAD_CATALOGS[case](formula)
    path = _write(tmp_path / "catalog.json", {"michaelis_menten": formula})

    with pytest.raises(CatalogError, match="michaelis_menten"):
        load_catalog(path)
    schema = json.loads(SCHEMA.read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate({"michaelis_menten": formula})


def test_empty_catalog_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="at least one formula"):
        load_catalog(_write(tmp_path / "catalog.json", {}))


def test_unreadable_json_names_the_file(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{not json")

    with pytest.raises(CatalogError, match=re.escape("catalog.json: cannot read JSON")):
        load_catalog(path)


def test_narrative_needs_nonempty_citations(tmp_path: Path) -> None:
    narrative = {**NARRATIVE_ENTRY, "citations": []}

    with pytest.raises(CatalogError, match="citations must be a non-empty list"):
        load_narratives(_write(tmp_path / "narratives.json", {"michaelis_menten": narrative}))


def test_registration_refuses_a_formula_without_a_narrative(
    tmp_path: Path, fresh_registry: dict[str, dict[str, registry.EquationFactory]]
) -> None:
    catalog = _write(tmp_path / "catalog.json", {"michaelis_menten": FORMULA})
    narratives = _write(tmp_path / "narratives.json", {"other": NARRATIVE_ENTRY})

    with pytest.raises(CatalogError, match="formulas without a narrative \\['michaelis_menten'\\]"):
        register_catalog_topic("demo", __name__, catalog, narratives, "templates/demo/src/model.py")
    assert fresh_registry == {}


def test_registration_builds_equations_with_their_math_trace_source(
    tmp_path: Path, fresh_registry: dict[str, dict[str, registry.EquationFactory]]
) -> None:
    catalog = _write(tmp_path / "catalog.json", {"michaelis_menten": FORMULA})
    narratives = _write(tmp_path / "narratives.json", {"michaelis_menten": NARRATIVE_ENTRY})

    register_catalog_topic("demo", __name__, catalog, narratives, "templates/demo/src/model.py")

    eq = registry.get("demo", "michaelis_menten")
    assert eq.id == "demo.michaelis_menten"
    assert eq.name == "Michaelis-Menten Equation"
    assert eq.source == ("templates/demo/src/model.py", 32)


def test_registration_refuses_a_second_topic_with_the_same_name(
    tmp_path: Path, fresh_registry: dict[str, dict[str, registry.EquationFactory]]
) -> None:
    catalog = _write(tmp_path / "catalog.json", {"michaelis_menten": FORMULA})
    narratives = _write(tmp_path / "narratives.json", {"michaelis_menten": NARRATIVE_ENTRY})
    register_catalog_topic("demo", __name__, catalog, narratives, "templates/demo/src/model.py")

    with pytest.raises(ValueError, match=re.escape("Duplicate equation demo.michaelis_menten")):
        register_catalog_topic("demo", __name__, catalog, narratives, "templates/demo/src/model.py")


def test_narratives_file_matches_the_snapshot_keys() -> None:
    assert load_narratives(NARRATIVE).keys() == load_catalog(CATALOG).keys()
