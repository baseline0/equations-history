"""Consumer-side contracts: the producers' artifacts must match the schemas this repo owns in contracts/."""

import json

import jsonschema
import pytest

from equations_history.constants import REPO_ROOT

pytestmark = pytest.mark.unit

CONTRACTS = REPO_ROOT / "contracts"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def schema(name: str) -> dict:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def test_schemas_are_valid_json_schema() -> None:
    for name in ("citation_graph.schema.json", "tex_manifest.schema.json"):
        jsonschema.Draft202012Validator.check_schema(schema(name))


def test_tex_manifest_fixtures_match_the_contract() -> None:
    manifests = sorted(FIXTURES.glob("tex_manifest/*/manifest.json"))
    assert manifests, "no TeX manifest fixture to check"
    validator = jsonschema.Draft202012Validator(schema("tex_manifest.schema.json"))
    for path in manifests:
        errors = list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))))
        assert not errors, f"{path.name}: {errors[0].message}"


def test_citation_graph_contract_accepts_a_minimal_graph_and_rejects_a_malformed_node_id() -> None:
    validator = jsonschema.Draft202012Validator(schema("citation_graph.schema.json"))
    good = {
        "nodes": ["2505.05283v3", "2508.00083v2"],
        "edges": [["2505.05283v3", "2508.00083v2"]],
        "sources": {"openalex": 0, "text_arxiv_ids": 1, "bibliography_titles": 0},
    }
    assert not list(validator.iter_errors(good))
    bad_id = {**good, "nodes": ["not-an-arxiv-id"]}
    assert list(validator.iter_errors(bad_id)), "a non-arXiv node id must be rejected"
