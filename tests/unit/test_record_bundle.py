"""Record bundles: additive verification, stable crosswalk ids and review-aware narrative chunks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from typer.testing import CliRunner

from equations_history.cli import app
from equations_history.constants import FORMULA_RECORD_EXT_SCHEMA_PATH, REPO_ROOT
from equations_history.formula_catalog import CatalogError, verify_catalog_snapshot
from equations_history.record_bundle import (
    build_bundle,
    build_extension,
    record_sha256,
    validate_extension,
)

pytestmark = pytest.mark.unit

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "formula_record" / "michaelis-menten.json"
runner = CliRunner()


def _record() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _provenance() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_commit": "d4f951b",
        "source_repo": "math-trace",
        "equations": {
            "michaelis_menten": {
                "id": "math-trace/michaelis_menten",
                "expr_hash": "sha256:" + "ab" * 32,
                "holds": True,
            }
        },
        "formal_claims": [
            {"claim_id": "C-mm", "theorem_path": "Theorem.mm", "theorem_sha256": "cd" * 32, "source_commit": "d4f951b"}
        ],
        "literature_claims": [{"paperId": "quant-ph-9605043", "claimId": "C-steane-1996-code"}],
    }


def test_the_extension_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(FORMULA_RECORD_EXT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_an_extension_can_carry_verification_and_a_pointer_only_stack_tag() -> None:
    ext = build_extension(_record(), _provenance(), formula="michaelis_menten", stacks_tag="0ELT")

    assert validate_extension(ext) == []
    assert ext["record_sha256"] == record_sha256(_record())
    assert ext["verification"]["holds"] is True
    assert "symbolic_verified" in ext["verification"]["statuses"]
    assert ext["verification"]["claims"][0]["claim_id"] == "C-mm"
    stacks = [item for item in ext["external"] if item["kind"] == "stacks"]
    assert stacks and stacks[0]["licence_status"] == "RESTRICTED"
    assert "data/tag/0ELT" in stacks[0]["url"]


def test_a_bundle_derives_a_crosswalk_without_changing_the_record() -> None:
    bundle = build_bundle("michaelis-menten")

    ids = bundle["identity"]
    assert ids["record_id"] == ids["slug"] == "michaelis-menten"
    assert ids["knowledge_id"] == "formula-michaelis-menten"
    assert ids["rag_record_key"].startswith("slug:") or ids["rag_record_key"].startswith("sha256:")
    assert bundle["record"]["id"] == "michaelis-menten"
    assert bundle["narrative_text"].startswith(f"[formula {ids['rag_record_key']}]")
    assert "Equation: " in bundle["narrative_text"]
    assert bundle["review"]["current"] is True


def test_a_stale_manifest_is_refused_at_load_time(tmp_path: Path) -> None:
    catalog = tmp_path / "biochemistry.json"
    catalog.write_text(
        json.dumps({"formula": {"latex": "x", "description": "d", "source_line": 1, "assumptions": "", "units": ""}})
    )
    manifest = tmp_path / "biochemistry.manifest.json"
    manifest.write_text(json.dumps({"source": "math-trace x", "source_commit": "abc", "sha256": "0" * 64}))

    with pytest.raises(CatalogError, match="does not match manifest"):
        verify_catalog_snapshot(catalog, manifest)


def test_a_current_manifest_is_accepted(tmp_path: Path) -> None:
    catalog = tmp_path / "biochemistry.json"
    payload = {"formula": {"latex": "x", "description": "d", "source_line": 1, "assumptions": "", "units": ""}}
    raw = json.dumps(payload)
    catalog.write_text(raw)
    manifest = tmp_path / "biochemistry.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "source": "math-trace x",
                "source_commit": "abc",
                "sha256": hashlib.sha256(raw.encode()).hexdigest(),
            }
        )
    )

    assert verify_catalog_snapshot(catalog, manifest)["source_commit"] == "abc"


def test_the_cli_wires_provenance_identity_and_writes_the_sidecar(tmp_path: Path) -> None:
    provenance = tmp_path / "equation_provenance.json"
    provenance.write_text(json.dumps(_provenance()))
    out = tmp_path / "record.json"
    ext_out = tmp_path / "record.ext.json"

    result = runner.invoke(
        app,
        [
            "record",
            "assemble",
            "--catalog",
            str(REPO_ROOT / "src/equations_history/catalogs/biochemistry.json"),
            "--narrative",
            str(REPO_ROOT / "src/equations_history/narratives/biochemistry.json"),
            "--formula",
            "michaelis_menten",
            "--id",
            "michaelis-menten",
            "--source-file",
            "templates/biochemistry/src/model.py",
            "--paper-store",
            str(REPO_ROOT / "tests/fixtures/paper_store"),
            "--out",
            str(out),
            "--provenance",
            str(provenance),
            "--stacks-tag",
            "0ELT",
            "--ext-out",
            str(ext_out),
        ],
    )

    assert result.exit_code == 0, result.output
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["provenance"]["code"]["expr_hash"] == "sha256:" + "ab" * 32
    assert record["provenance"]["code"]["commit"] == "d4f951b"
    assert validate_extension(json.loads(ext_out.read_text(encoding="utf-8"))) == []


def test_the_cli_bundle_command_prints_the_merged_view() -> None:
    result = runner.invoke(app, ["record", "bundle", "--id", "michaelis-menten"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["identity"]["knowledge_id"] == "formula-michaelis-menten"


def test_build_extension_refuses_unknown_formula() -> None:
    with pytest.raises(CatalogError, match="no formula 'missing'"):
        build_extension(_record(), _provenance(), formula="missing")


def test_validate_extension_reports_contract_violations() -> None:
    bad = {"record_id": "michaelis-menten"}  # missing required fields per schema

    problems = validate_extension(bad)

    assert problems
    assert any("record_sha256" in p or "required" in p.lower() or p for p in problems)


def test_build_bundle_refuses_unknown_record() -> None:
    with pytest.raises(CatalogError, match="unknown formula record 'does-not-exist'"):
        build_bundle("does-not-exist")
