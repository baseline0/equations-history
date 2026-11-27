"""Record bundles: the additive view consumers actually need.

formula-record/1 stays unchanged so published bytes and human reviews do not move. A sidecar
(``formula-records-full/<id>.ext.json``) carries verification, pointer-only external context and the
record digest. ``build_bundle`` joins the record, its sidecar and the review pin into one stable
object, and derives the crosswalk ids that math-trace, tool-lit-review and tool-rag all use.

Everything here is pure file/JSON work. No network call is made; a Stacks pointer never fetches.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Canonical record digest is SHA-256 of deterministic JSON (sorted keys, compact separators, UTF-8) | crosswalk/refresh contract | `canonical_json`, `record_sha256`; `tests/unit/test_record_bundle.py::test_an_extension_can_carry_verification_and_a_pointer_only_stack_tag` (digest equality) |
| Review pin `current` compares raw public file bytes SHA-256, not canonicalized record digest | publication review contract | `file_sha256`, `review_for`; `tests/unit/test_record_bundle.py::test_a_bundle_derives_a_crosswalk_without_changing_the_record` |
| Extension sidecar must satisfy `contracts/formula_record_ext.schema.json`; invalid/malformed sidecars raise `CatalogError` | `contracts/formula_record_ext.schema.json` | `_extension_validator`, `validate_extension`, `load_extension`; `tests/unit/test_record_bundle.py::test_the_extension_schema_is_valid_draft_2020_12`, `test_an_extension_can_carry_verification_and_a_pointer_only_stack_tag` |
| Bundle build refuses unknown records and records failing `record_problems`; invalid extension is an error | bundle assembly contract | `_load_record`, `build_bundle`; `tests/unit/test_record_bundle.py::test_a_bundle_derives_a_crosswalk_without_changing_the_record` (happy path), CLI bundle/assemble coverage |
| Crosswalk ids are derived (record_id/slug/expr_hash/math_trace_id/rag_record_key/knowledge_id/stacks_tag), never hand-maintained | crosswalk contract | `identity`, `build_bundle`; `tests/unit/test_record_bundle.py::test_a_bundle_derives_a_crosswalk_without_changing_the_record` |
| Verification exposes `holds`, known status names present in sidecar only; absent statuses omitted (never false) | verification contract | `STATUSES`, `verification`; `tests/unit/test_record_bundle.py::test_an_extension_can_carry_verification_and_a_pointer_only_stack_tag` |
| External context is pointer-only; Stacks pointers are marked `RESTRICTED` and never fetched | external-content contract | `build_extension`, `external_context`; `tests/unit/test_record_bundle.py::test_an_extension_can_carry_verification_and_a_pointer_only_stack_tag` |
| `build_extension` refuses provenance missing the named formula; built extension must validate | provenance-join contract | `build_extension`; `tests/unit/test_record_bundle.py::test_the_cli_wires_provenance_identity_and_writes_the_sidecar` (happy path) |
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from typing import Any

import jsonschema

from equations_history.constants import (
    FORMULA_RECORD_EXT_SCHEMA_PATH,
    FULL_RECORDS_DIR,
    PUBLIC_RECORDS_DIR,
    REVIEWS_PATH,
)
from equations_history.formula_catalog import CatalogError
from equations_history.formula_record import public_view, record_problems

STATUSES = (
    "source_verified",
    "transcription_verified",
    "symbolic_verified",
    "numerically_verified",
    "formally_verified",
    "historical_interpretation",
)


def canonical_json(value: Any) -> str:
    """A deterministic JSON string: sorted keys, no incidental whitespace."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_sha256(record: Mapping[str, Any]) -> str:
    """Content digest of a record: stable across formatting, used for crosswalk and RAG refresh."""
    return hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    """SHA-256 of raw bytes, matching the publication review pin in reviews.json."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@cache
def _extension_validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(FORMULA_RECORD_EXT_SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


def validate_extension(ext: Mapping[str, Any]) -> list[str]:
    """Every contract violation in an extension sidecar, with JSON paths. Empty means valid."""
    errors = sorted(_extension_validator().iter_errors(ext), key=lambda error: list(error.absolute_path))
    return [f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in errors]


def extension_path(record_id: str) -> Path:
    """Where the sidecar for ``record_id`` lives, beside the full record."""
    return FULL_RECORDS_DIR / f"{record_id}.ext.json"


def load_extension(record_id: str) -> dict[str, Any] | None:
    """The parsed extension sidecar, or None when the record has none. Invalid sidecars are errors."""
    path = extension_path(record_id)
    if not path.is_file():
        return None
    try:
        ext = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"{path.name}: cannot read extension: {error}") from error
    if not isinstance(ext, dict):
        raise CatalogError(f"{path.name}: an extension is a JSON object")
    problems = validate_extension(ext)
    if problems:
        raise CatalogError(f"{path.name}: " + "; ".join(problems))
    return ext


def _load_record(record_id: str, *, public: bool) -> dict[str, Any]:
    """The full record by default; the reviewed public view when ``public`` is set."""
    directory = PUBLIC_RECORDS_DIR if public else FULL_RECORDS_DIR
    path = directory / f"{record_id}.json"
    if not path.is_file() and not public:
        path = PUBLIC_RECORDS_DIR / f"{record_id}.json"
    if not path.is_file():
        raise CatalogError(f"unknown formula record {record_id!r}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"{path.name}: cannot read record: {error}") from error
    if not isinstance(record, dict):
        raise CatalogError(f"{path.name}: a formula record is a JSON object")
    return record


def read_reviews() -> dict[str, Any]:
    """The publication review pins, keyed by record slug. A missing file means no reviews."""
    if not REVIEWS_PATH.is_file():
        return {}
    try:
        data = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"{REVIEWS_PATH.name}: cannot read reviews: {error}") from error
    return data if isinstance(data, dict) else {}


def review_for(record_id: str) -> dict[str, Any] | None:
    """The review pin for a record, with ``current`` showing whether it still matches the public bytes.

    The publication gate hashes the reviewed file's raw bytes, so this check must do the same; the
    bundle's own ``record_sha256`` is a separate content digest used for identity and refresh.
    """
    review = read_reviews().get(record_id)
    if not isinstance(review, dict):
        return None
    public_file = PUBLIC_RECORDS_DIR / f"{record_id}.json"
    current = public_file.is_file() and review.get("sha256") == file_sha256(public_file)
    return {**review, "current": current}


def identity(record: Mapping[str, Any], ext: Mapping[str, Any] | None) -> dict[str, Any]:
    """The crosswalk. Every id is derived, never hand-maintained in two repos."""
    slug = str(record.get("id", ""))
    code = record.get("provenance", {}).get("code", {}) if isinstance(record.get("provenance"), Mapping) else {}
    expr_hash = code.get("expr_hash") or (ext or {}).get("expr_hash")
    external = (ext or {}).get("external", []) or []
    stacks = [item for item in external if isinstance(item, Mapping) and item.get("kind") == "stacks"]
    math_trace_id = (ext or {}).get("math_trace_id") or (f"math-trace/{slug.replace('-', '_')}" if code else None)
    return {
        "record_id": slug,
        "slug": slug,
        "expr_hash": expr_hash,
        "math_trace_id": math_trace_id,
        "rag_record_key": expr_hash or f"slug:{slug}",
        "knowledge_id": f"formula-{slug}",
        "stacks_tag": stacks[0].get("id") if stacks else None,
    }


def verification(ext: Mapping[str, Any] | None) -> dict[str, Any]:
    """Verification from the sidecar. Absent statuses are omitted, never set to false."""
    raw = (ext or {}).get("verification") or {}
    statuses = raw.get("statuses") or {}
    return {
        "holds": raw.get("holds"),
        "statuses": {name: statuses[name] for name in STATUSES if name in statuses},
        "claims": list(raw.get("claims") or []),
    }


def external_context(ext: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Pointer-only external references. Licence status is stored, not inferred at read time."""
    return list((ext or {}).get("external") or [])


def narrative_chunk(record: Mapping[str, Any], ids: Mapping[str, Any], ext: Mapping[str, Any] | None) -> str:
    """One chunk suitable for tool-rag: identity, location, history and the equation itself."""
    code = record.get("provenance", {}).get("code", {}) if isinstance(record.get("provenance"), Mapping) else {}
    literature = (
        record.get("provenance", {}).get("literature", {}) if isinstance(record.get("provenance"), Mapping) else {}
    )
    narrative = record.get("narrative", {}) if isinstance(record.get("narrative"), Mapping) else {}
    parts = [f"[formula {ids['rag_record_key']}]", f"Record: {ids['record_id']}"]
    if ids.get("expr_hash"):
        parts.append(f"ExprHash: {ids['expr_hash']}")
    if literature:
        parts.append(f"Paper: {literature.get('paper_store_id')} {literature.get('version')}")
        parts.append(f"Locator: {literature.get('locator')}")
    if code:
        parts.append(f"Location: {code.get('repo')}:{code.get('file')}:{code.get('source_line')}")
    if narrative.get("concepts"):
        parts.append("Concepts: " + ", ".join(str(item) for item in narrative["concepts"]))
    if narrative.get("history"):
        parts.append("Context: " + str(narrative["history"]).strip())
    parts.append(f"Equation: {record.get('core', {}).get('latex', '')}")
    if narrative.get("citations"):
        parts.append("Citations: " + "; ".join(str(item) for item in narrative["citations"]))
    for pointer in external_context(ext):
        parts.append(f"External: {pointer.get('kind')}:{pointer.get('id')} ({pointer.get('licence_status')})")
    return "\n".join(parts)


def build_bundle(record_id: str, *, public: bool = False) -> dict[str, Any]:
    """Join a formula record, its extension and its review pin into one addressable bundle.

    Raises CatalogError for an unknown record, a malformed extension, or a record that fails its own contract;
    a caller can turn that into an envelope error without leaking a traceback.
    """
    record = _load_record(record_id, public=public)
    problems = record_problems(record)
    if problems:
        raise CatalogError(f"{record_id}: " + "; ".join(problems))
    ext = load_extension(record_id)
    digest = record_sha256(record)
    ids = identity(record, ext)
    return {
        "schema_version": "1.0",
        "record_id": record_id,
        "record_sha256": digest,
        "record": record,
        "public": public_view(record),
        "identity": ids,
        "verification": verification(ext),
        "external": external_context(ext),
        "review": review_for(record_id),
        "narrative_text": narrative_chunk(record, ids, ext),
    }


def build_extension(
    record: Mapping[str, Any],
    provenance: Mapping[str, Any],
    *,
    formula: str,
    stacks_tag: str | None = None,
) -> dict[str, Any]:
    """Build an extension sidecar from math-trace's additive provenance artifact.

    ``provenance`` is math-trace's ``equation_provenance.json``. The record itself is never rewritten:
    verification states are added in the sidecar, and a Stacks tag is a pointer, not a fetched source.
    """
    raw_equations = provenance.get("equations")
    equations: dict[str, Any] = dict(raw_equations) if isinstance(raw_equations, Mapping) else {}
    entry = equations.get(formula)
    if not isinstance(entry, Mapping):
        raise CatalogError(f"provenance artifact has no formula {formula!r}")
    digest = record_sha256(record)
    exposures: dict[str, Any] = {"holds": entry.get("holds")}
    supplied = entry.get("verification")
    if isinstance(supplied, Mapping):
        exposures["statuses"] = dict(supplied)
    else:
        derived: dict[str, Any] = {}
        if entry.get("holds") is True:
            derived["symbolic_verified"] = {"by": "math-trace", "note": "residual check passed"}
        claims = provenance.get("formal_claims") or []
        if claims:
            derived["formally_verified"] = {"by": "Lean", "note": f"{len(claims)} formal claim(s) exported"}
        exposures["statuses"] = derived
    exposures["claims"] = [
        {key: claim[key] for key in ("claim_id", "theorem_path", "theorem_sha256", "source_commit") if key in claim}
        for claim in (provenance.get("formal_claims") or [])
        if isinstance(claim, Mapping) and "claim_id" in claim
    ]

    external: list[dict[str, Any]] = []
    for claim in provenance.get("literature_claims") or []:
        if not isinstance(claim, Mapping):
            continue
        paper_id = claim.get("paperId") or claim.get("paper_id") or claim.get("id")
        if paper_id:
            external.append({"kind": "paper", "id": str(paper_id), "licence_status": "UNKNOWN"})
    if stacks_tag:
        external.append(
            {
                "kind": "stacks",
                "id": stacks_tag,
                "url": f"https://stacks.math.columbia.edu/data/tag/{stacks_tag}",
                "licence_status": "RESTRICTED",
                "note": "Pointer only. Stacks content is GNU FDL; index only an approved snapshot.",
            }
        )

    ext: dict[str, Any] = {
        "record_id": str(record.get("id", "")),
        "record_sha256": digest,
        "math_trace_id": str(entry.get("id") or f"math-trace/{formula}"),
        "verification": exposures,
        "external": external,
    }
    if entry.get("expr_hash"):
        ext["expr_hash"] = str(entry["expr_hash"])
    problems = validate_extension(ext)
    if problems:
        raise CatalogError("built extension is invalid: " + "; ".join(problems))
    return ext


def write_extension(ext: Mapping[str, Any], out: Path) -> Path:
    """Write a validated extension sidecar with a trailing newline."""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ext, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
