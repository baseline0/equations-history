"""Formula record v1: the contract, unit consistency, the literature licence rule, the public view and the CLI."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from typer.testing import CliRunner

from equations_history.cli import app
from equations_history.constants import FORMULA_RECORD_SCHEMA_PATH, REPO_ROOT
from equations_history.formula_catalog import load_catalog, load_narratives
from equations_history.formula_record import (
    AssemblyError,
    assemble_record,
    check_record,
    literature_is_open,
    literature_problems,
    public_view,
    record_problems,
    unit_problems,
    units_agree,
    validate_record,
)
from equations_history.paper_store import PaperStore

pytestmark = pytest.mark.unit

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "formula_record"
PILOT = FIXTURES / "navier-stokes-momentum-3d.json"
STORE = FIXTURES.parent / "paper_store"
OPEN_LICENCE = "https://creativecommons.org/licenses/by/4.0"


@pytest.fixture
def pilot() -> dict[str, Any]:
    """The Navier-Stokes momentum record, freshly parsed so each test may mutate its own copy."""
    return json.loads(PILOT.read_text(encoding="utf-8"))


def test_the_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(FORMULA_RECORD_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_the_pilot_record_is_valid(pilot: dict[str, Any]) -> None:
    assert validate_record(pilot) == []
    assert record_problems(pilot) == []


@pytest.mark.parametrize("fixture", sorted(FIXTURES.glob("*.json")), ids=lambda path: path.name)
def test_every_fixture_record_is_valid(fixture: Path) -> None:
    assert record_problems(json.loads(fixture.read_text(encoding="utf-8"))) == []


def test_a_literature_block_is_optional(pilot: dict[str, Any]) -> None:
    assert "literature" not in pilot["provenance"]
    assert validate_record(pilot) == []


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("provenance", "literature"), {"paper_store_id": "2610.23820", "version": 1, "locator": "page 4"}),
        (("provenance", "literature"), {"paper_store_id": "2610.23820", "version": "v1"}),
        (("provenance", "literature"), {"paper_store_id": "arxiv-0911-4475v2", "version": "v2", "locator": "p. 4"}),
        (
            ("provenance", "literature"),
            {"paper_store_id": "2610.23820", "version": "v1", "locator": "p. 4", "licence_allowed": True},
        ),
        (("id",), "Navier Stokes"),
        (("provenance", "code", "source_line"), 0),
        (("core", "licence"), "CC-BY"),
        (("narrative", "year"), True),
    ],
    ids=[
        "integer-version",
        "literature-without-locator",
        "malformed-paper-id",
        "self-attested-licence-flag",
        "id-with-spaces",
        "source-line-below-one",
        "unknown-core-field",
        "boolean-year",
    ],
)
def test_the_contract_rejects_malformed_records(pilot: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    record = copy.deepcopy(pilot)
    target: Any = record
    for key in path[:-1]:
        target = target.setdefault(key, {})
    target[path[-1]] = value
    assert validate_record(record), f"{'/'.join(path)} should be rejected"


def test_units_with_the_same_dimensions_agree() -> None:
    assert units_agree("kg / (m^2 s^2)", "N / m^3")
    assert units_agree("kg/(m^2 s^2)", "Pa / m")


def test_units_with_different_dimensions_are_reported(pilot: dict[str, Any]) -> None:
    pilot["core"]["units"]["rhs"] = "N / m^2"
    problems = record_problems(pilot)
    assert problems and "dimension mismatch" in problems[0]


def test_units_pint_cannot_parse_are_reported_not_raised() -> None:
    problems = unit_problems({"lhs": "kg / (m^2 s^2)", "rhs": "not_a_unit_xyz"})
    assert problems and problems[0].startswith("units cannot be parsed")


def test_a_record_that_fails_the_contract_is_not_unit_checked(pilot: dict[str, Any]) -> None:
    pilot["core"]["units"]["rhs"] = 5
    problems = record_problems(pilot)
    assert problems and all("dimension" not in problem for problem in problems)


@pytest.mark.parametrize(
    "licence",
    [
        OPEN_LICENCE,
        "https://creativecommons.org/licenses/by-sa/4.0",
        "https://creativecommons.org/publicdomain/zero/1.0",
    ],
)
def test_the_three_open_licences_are_accepted(licence: str) -> None:
    assert literature_is_open(licence)


@pytest.mark.parametrize(
    "licence",
    ["https://creativecommons.org/licenses/by-nc/4.0", "https://creativecommons.org/licenses/by/4.0/", None, ""],
    ids=["non-commercial", "trailing-slash-is-not-canonical", "missing", "empty"],
)
def test_any_other_licence_is_refused(licence: str | None) -> None:
    assert not literature_is_open(licence)


def test_the_public_view_drops_internal_provenance_and_keeps_the_narrative(pilot: dict[str, Any]) -> None:
    view = public_view(pilot)
    assert view["provenance"] == {"code": {"repo": "math-trace"}}
    assert view["narrative"] == pilot["narrative"]
    assert view["core"] == pilot["core"]
    assert view["id"] == pilot["id"]


def test_the_public_view_keeps_a_literature_locator_but_no_tex(pilot: dict[str, Any]) -> None:
    pilot["provenance"]["literature"] = {"paper_store_id": "2610.23820", "version": "v1", "locator": "page 4"}
    view = public_view(pilot)
    assert view["provenance"]["literature"] == {"paper_store_id": "2610.23820", "version": "v1", "locator": "page 4"}


def test_the_public_view_does_not_mutate_its_input(pilot: dict[str, Any]) -> None:
    before = copy.deepcopy(pilot)
    public_view(pilot)
    assert pilot == before


def test_the_cli_validates_the_pilot_with_exit_zero() -> None:
    result = CliRunner().invoke(app, ["record", "validate", "--path", str(PILOT), "--paper-store", str(STORE)])
    assert result.exit_code == 0, result.output
    assert "valid" in result.output


def test_the_cli_reports_every_problem_with_exit_one(tmp_path: Path, pilot: dict[str, Any]) -> None:
    pilot["core"]["units"]["rhs"] = "N / m^2"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(pilot), encoding="utf-8")
    result = CliRunner().invoke(app, ["record", "validate", "--path", str(bad), "--paper-store", str(STORE)])
    assert result.exit_code == 1
    assert "dimension mismatch" in result.output


def test_the_cli_public_writes_only_public_fields(tmp_path: Path) -> None:
    out = tmp_path / "public.json"
    result = CliRunner().invoke(
        app, ["record", "public", "--path", str(PILOT), "--paper-store", str(STORE), "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    written = json.loads(out.read_text(encoding="utf-8"))
    assert "file" not in written["provenance"]["code"]
    assert "source_line" not in written["provenance"]["code"]


def test_the_cli_public_refuses_an_invalid_record_and_writes_nothing(tmp_path: Path, pilot: dict[str, Any]) -> None:
    pilot["id"] = "Not A Slug"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(pilot), encoding="utf-8")
    out = tmp_path / "public.json"
    result = CliRunner().invoke(
        app, ["record", "public", "--path", str(bad), "--paper-store", str(STORE), "--out", str(out)]
    )
    assert result.exit_code == 1
    assert not out.exists()


MATH_TRACE_OUTPUT = FIXTURES.parent / "math_trace" / "biochemistry.equations.json"
BIOCHEMISTRY_NARRATIVES = REPO_ROOT / "src" / "equations_history" / "narratives" / "biochemistry.json"
BIOCHEMISTRY_SNAPSHOT = REPO_ROOT / "src" / "equations_history" / "catalogs" / "biochemistry.json"


def test_the_assembler_reproduces_the_michaelis_menten_record_from_its_sources() -> None:
    entries = load_catalog(MATH_TRACE_OUTPUT)
    narratives = load_narratives(BIOCHEMISTRY_NARRATIVES)
    record = assemble_record(
        "michaelis-menten",
        entries["michaelis_menten"],
        narratives["michaelis_menten"],
        source_file="templates/biochemistry/src/model.py",
        store=PaperStore(STORE),
    )
    assert record == json.loads((FIXTURES / "michaelis-menten.json").read_text(encoding="utf-8"))


def test_the_assembler_refuses_a_formula_whose_units_math_trace_has_not_declared() -> None:
    entries = load_catalog(MATH_TRACE_OUTPUT)
    narratives = load_narratives(BIOCHEMISTRY_NARRATIVES)
    with pytest.raises(AssemblyError, match="units_lhs and units_rhs"):
        assemble_record(
            "enzyme-mechanism",
            entries["enzyme_mechanism"],
            narratives["enzyme_mechanism"],
            source_file="templates/biochemistry/src/model.py",
            store=PaperStore(STORE),
        )


def test_the_biochemistry_snapshot_carries_the_structured_units() -> None:
    assert load_catalog(BIOCHEMISTRY_SNAPSHOT)["michaelis_menten"].units_lhs == "umol / min"


def test_the_assembler_accepts_max_velocity_once_its_units_are_declared() -> None:
    entries = load_catalog(BIOCHEMISTRY_SNAPSHOT)
    narratives = load_narratives(BIOCHEMISTRY_NARRATIVES)
    record = assemble_record(
        "max-velocity",
        entries["max_velocity"],
        narratives["max_velocity"],
        source_file="templates/biochemistry/src/model.py",
        store=PaperStore(STORE),
    )
    assert record["core"]["units"] == {"lhs": "umol / min", "rhs": "s^-1 * umol"}


MATH_TRACE = REPO_ROOT.parent / "math-trace"


@pytest.mark.skipif(not MATH_TRACE.is_dir(), reason="needs the math-trace checkout beside this repo")
def test_the_michaelis_menten_source_line_points_at_its_formula_call() -> None:
    record = json.loads((FIXTURES / "michaelis-menten.json").read_text(encoding="utf-8"))
    code = record["provenance"]["code"]
    lines = (MATH_TRACE / code["file"]).read_text(encoding="utf-8").splitlines()
    assert "Formula(" in lines[code["source_line"] - 1]


def _with_literature(pilot: dict[str, Any], arxiv_id: str, version: str = "v1") -> dict[str, Any]:
    pilot["provenance"]["literature"] = {"paper_store_id": arxiv_id, "version": version, "locator": "page 4"}
    return pilot


def test_a_literature_block_on_an_open_current_paper_passes(pilot: dict[str, Any]) -> None:
    assert literature_problems(_with_literature(pilot, "2610.23820"), PaperStore(STORE)) == []


def test_a_literature_block_on_a_restricted_paper_is_refused(pilot: dict[str, Any]) -> None:
    problems = literature_problems(_with_literature(pilot, "2610.99999"), PaperStore(STORE))
    assert problems and "restricted" in problems[0]


def test_a_literature_block_on_an_unknown_paper_is_refused(pilot: dict[str, Any]) -> None:
    problems = literature_problems(_with_literature(pilot, "2610.00001"), PaperStore(STORE))
    assert problems and "2610.00001" in problems[0]


def test_a_literature_block_pinning_an_old_version_is_refused(pilot: dict[str, Any]) -> None:
    problems = literature_problems(_with_literature(pilot, "2610.23820", version="v0"), PaperStore(STORE))
    assert problems and "latest is v1" in problems[0]


def test_a_record_without_literature_needs_no_paper_store(pilot: dict[str, Any], tmp_path: Path) -> None:
    assert literature_problems(pilot, PaperStore(tmp_path)) == []


def test_check_record_skips_the_paper_store_when_the_record_is_malformed(pilot: dict[str, Any]) -> None:
    pilot["id"] = "Not A Slug"
    _with_literature(pilot, "2610.99999")
    problems = check_record(pilot, PaperStore(STORE))
    assert problems and all("restricted" not in problem for problem in problems)


def test_the_cli_refuses_a_record_whose_literature_is_restricted(tmp_path: Path, pilot: dict[str, Any]) -> None:
    bad = tmp_path / "restricted.json"
    bad.write_text(json.dumps(_with_literature(pilot, "2610.99999")), encoding="utf-8")
    result = CliRunner().invoke(app, ["record", "validate", "--path", str(bad), "--paper-store", str(STORE)])
    assert result.exit_code == 1
    assert "restricted" in result.output


def _assemble_args(formula: str, record_id: str, out: Path) -> list[str]:
    return [
        "record",
        "assemble",
        "--catalog",
        str(MATH_TRACE_OUTPUT),
        "--narrative",
        str(BIOCHEMISTRY_NARRATIVES),
        "--formula",
        formula,
        "--id",
        record_id,
        "--source-file",
        "templates/biochemistry/src/model.py",
        "--paper-store",
        str(STORE),
        "--out",
        str(out),
    ]


def test_the_cli_assembles_the_pilot_record(tmp_path: Path) -> None:
    out = tmp_path / "michaelis-menten.json"
    result = CliRunner().invoke(app, _assemble_args("michaelis_menten", "michaelis-menten", out))
    assert result.exit_code == 0, result.output
    assert json.loads(out.read_text(encoding="utf-8"))["id"] == "michaelis-menten"


def test_the_cli_refuses_a_formula_without_declared_units_and_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "enzyme-mechanism.json"
    result = CliRunner().invoke(app, _assemble_args("enzyme_mechanism", "enzyme-mechanism", out))
    assert result.exit_code == 1
    assert "units_lhs and units_rhs" in result.output
    assert not out.exists()


def test_the_assembler_joins_an_open_literature_reference_when_given() -> None:
    entries = load_catalog(MATH_TRACE_OUTPUT)
    narratives = load_narratives(BIOCHEMISTRY_NARRATIVES)
    record = assemble_record(
        "michaelis-menten",
        entries["michaelis_menten"],
        narratives["michaelis_menten"],
        source_file="templates/biochemistry/src/model.py",
        store=PaperStore(STORE),
        literature={"paper_store_id": "2610.23820", "version": "v1", "locator": "page 4"},
    )
    assert record["provenance"]["literature"] == {"paper_store_id": "2610.23820", "version": "v1", "locator": "page 4"}


def test_the_assembler_refuses_a_literature_reference_to_a_restricted_paper() -> None:
    entries = load_catalog(MATH_TRACE_OUTPUT)
    narratives = load_narratives(BIOCHEMISTRY_NARRATIVES)
    with pytest.raises(AssemblyError, match="restricted"):
        assemble_record(
            "michaelis-menten",
            entries["michaelis_menten"],
            narratives["michaelis_menten"],
            source_file="templates/biochemistry/src/model.py",
            store=PaperStore(STORE),
            literature={"paper_store_id": "2610.99999", "version": "v1", "locator": "page 4"},
        )


def test_the_cli_assembles_a_cited_record_with_its_literature_reference(tmp_path: Path) -> None:
    out = tmp_path / "cited.json"
    args = _assemble_args("michaelis_menten", "michaelis-menten", out)
    cited = [
        "record",
        "assemble-cited",
        *args[2:-2],
        "--literature-id",
        "2610.23820",
        "--literature-version",
        "v1",
        "--locator",
        "page 4",
        "--out",
        str(out),
    ]
    result = CliRunner().invoke(app, cited)
    assert result.exit_code == 0, result.output
    assert json.loads(out.read_text(encoding="utf-8"))["provenance"]["literature"]["paper_store_id"] == "2610.23820"
