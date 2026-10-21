"""Contract test: the paper store reader against the sample store that fleet-coordination owns (FORMAT.md v1).

The sample lives in the fleet-coordination checkout beside this repo. When that checkout is absent the whole
module is skipped with the expected path in the reason.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from equations_history.constants import REPO_ROOT
from equations_history.paper_store import (
    ALLOWED_LICENCES,
    STATUSES,
    PaperStore,
    RestrictedPaperError,
)

SAMPLE = REPO_ROOT.parent / "fleet-coordination" / "contracts" / "paper-store" / "sample"

pytestmark = pytest.mark.skipif(
    not SAMPLE.is_dir(),
    reason=f"fleet-coordination checkout not found beside this repo; expected the paper-store sample at {SAMPLE}",
)

# Every manifest field the contract lists, with the Python types the contract allows.
MANIFEST_FIELD_TYPES: dict[str, tuple[type, ...]] = {
    "schema_version": (int,),
    "arxiv_id": (str,),
    "version": (str,),
    "title": (str,),
    "doi": (str, type(None)),
    "licence": (str,),
    "pdf_sha256": (str, type(None)),
    "tex_sha256": (str, type(None)),
    "status": (str,),
    "fetched_at": (str,),
}


def _sample_manifests() -> list[tuple[Path, dict[str, Any]]]:
    manifests = []
    for paper_dir in sorted((SAMPLE / "papers").iterdir()):
        name = (paper_dir / "latest").read_text(encoding="utf-8").strip()
        manifests.append((paper_dir, json.loads((paper_dir / name).read_text(encoding="utf-8"))))
    return manifests


def _membership_rows() -> list[dict[str, str]]:
    lines = (SAMPLE / "catalog" / "membership.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def test_sample_manifests_carry_every_field_with_the_contract_type() -> None:
    manifests = _sample_manifests()
    assert manifests, "the sample holds no papers"
    for paper_dir, manifest in manifests:
        assert set(manifest) >= set(MANIFEST_FIELD_TYPES), f"{paper_dir.name}: missing fields"
        for field, types in MANIFEST_FIELD_TYPES.items():
            value = manifest[field]
            assert isinstance(value, types) and not (isinstance(value, bool)), (
                f"{paper_dir.name}: {field} is {value!r}, expected one of {types}"
            )


def test_sample_manifest_values_follow_the_contract_rules() -> None:
    for paper_dir, manifest in _sample_manifests():
        assert manifest["schema_version"] == 1
        assert manifest["arxiv_id"] == paper_dir.name
        assert manifest["status"] in STATUSES
        assert manifest["licence"] in ALLOWED_LICENCES
        datetime.fromisoformat(manifest["fetched_at"])  # ISO 8601 with offset; raises if not


def test_sample_blobs_hash_to_their_names() -> None:
    checked = 0
    for _, manifest in _sample_manifests():
        for field in ("pdf_sha256", "tex_sha256"):
            sha = manifest[field]
            if sha is None:
                continue
            path = SAMPLE / "blobs" / sha[:2] / sha
            assert path.is_file(), f"{field} blob missing: {path}"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
            checked += 1
    assert checked, "the sample holds no blob to check"


def test_reader_returns_the_sample_paper_with_its_pdf_present() -> None:
    store = PaperStore(SAMPLE)
    for paper_dir, expected in _sample_manifests():
        record = store.read_paper(paper_dir.name)

        assert record.manifest.arxiv_id == expected["arxiv_id"]
        assert record.manifest.version == expected["version"]
        assert record.manifest.pdf_sha256 == expected["pdf_sha256"]
        assert record.tex == (None if expected["tex_sha256"] is None else store.get_blob(expected["tex_sha256"]))


def test_every_membership_line_resolves_to_a_paper() -> None:
    store = PaperStore(SAMPLE)
    rows = _membership_rows()
    assert rows, "the sample membership file is empty"
    for row in rows:
        assert (SAMPLE / "papers" / row["arxiv_id"]).is_dir(), f"no paper directory for {row['arxiv_id']}"
        store.read_paper(row["arxiv_id"])
        assert row["arxiv_id"] in store.topic_papers(row["topic"])


def test_restricted_licence_is_refused_on_the_sample(tmp_path: Path) -> None:
    store_copy = tmp_path / "sample"
    shutil.copytree(SAMPLE, store_copy)
    for paper_dir in (store_copy / "papers").iterdir():
        name = (paper_dir / "latest").read_text(encoding="utf-8").strip()
        manifest_path = paper_dir / name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["licence"] = "https://creativecommons.org/licenses/by-nc/4.0"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    for row in _membership_rows():
        with pytest.raises(RestrictedPaperError):
            PaperStore(store_copy).read_paper(row["arxiv_id"])
