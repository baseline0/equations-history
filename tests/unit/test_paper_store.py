"""Tests for the paper store v1 reader. Offline: each test builds a small store under tmp_path."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from equations_history import paper_store
from equations_history.paper_store import (
    BrokenPaperError,
    PaperStore,
    RestrictedPaperError,
)

ARXIV = "2610.23820"
OPEN_LICENCE = "https://creativecommons.org/licenses/by/4.0"


def _put_blob(root: Path, data: bytes) -> str:
    sha = hashlib.sha256(data).hexdigest()
    path = root / "blobs" / sha[:2] / sha
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha


def _manifest(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": 1,
        "arxiv_id": ARXIV,
        "version": "v1",
        "title": "Test paper",
        "doi": None,
        "licence": OPEN_LICENCE,
        "pdf_sha256": None,
        "tex_sha256": None,
        "status": "saved",
        "fetched_at": "2026-10-20T00:00:00Z",
    }
    base.update(overrides)
    return base


def _write_paper(root: Path, manifest: dict[str, Any], arxiv_id: str = ARXIV) -> None:
    paper_dir = root / "papers" / arxiv_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    name = f"{manifest['version']}.json"
    (paper_dir / name).write_text(json.dumps(manifest), encoding="utf-8")
    (paper_dir / "latest").write_text(name + "\n", encoding="utf-8")


def _write_membership(root: Path, rows: list[tuple[str, str]]) -> None:
    catalog = root / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({"topic": topic, "arxiv_id": arxiv_id, "query": "q", "added_at": "2026-10-20T00:00:00Z"})
        for topic, arxiv_id in rows
    ]
    (catalog / "membership.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_paper_with_a_tex_blob_returns_the_blob_bytes(tmp_path: Path) -> None:
    tex = b"\\documentclass{article}\n"
    _write_paper(tmp_path, _manifest(tex_sha256=_put_blob(tmp_path, tex)))

    record = PaperStore(tmp_path).read_paper(ARXIV)

    assert record.tex == tex
    assert record.manifest.version == "v1"


@pytest.mark.parametrize("field", ["pdf_sha256", "tex_sha256"])
def test_manifest_with_a_missing_blob_is_reported_as_broken(tmp_path: Path, field: str) -> None:
    _write_paper(tmp_path, _manifest(**{field: "a" * 64}))

    with pytest.raises(BrokenPaperError, match="missing"):
        PaperStore(tmp_path).read_paper(ARXIV)


def test_blob_that_does_not_hash_to_its_name_is_broken(tmp_path: Path) -> None:
    sha = hashlib.sha256(b"the bytes the manifest expects").hexdigest()
    path = tmp_path / "blobs" / sha[:2] / sha
    path.parent.mkdir(parents=True)
    path.write_bytes(b"tampered bytes")
    _write_paper(tmp_path, _manifest(tex_sha256=sha))

    with pytest.raises(BrokenPaperError, match="does not hash"):
        PaperStore(tmp_path).read_paper(ARXIV)


@pytest.mark.parametrize(
    "licence",
    [
        "https://creativecommons.org/licenses/by-nc/4.0",
        "https://creativecommons.org/licenses/by/4.0/",
        "http://creativecommons.org/licenses/by/4.0",
        "https://example.org/all-rights-reserved",
        None,
    ],
)
def test_non_allowed_licence_is_refused(tmp_path: Path, licence: str | None) -> None:
    tex = b"restricted bytes"
    _write_paper(tmp_path, _manifest(licence=licence, tex_sha256=_put_blob(tmp_path, tex)))

    with pytest.raises(RestrictedPaperError):
        PaperStore(tmp_path).read_paper(ARXIV)


def test_manifest_without_a_licence_field_is_refused_as_restricted(tmp_path: Path) -> None:
    manifest = _manifest()
    del manifest["licence"]
    _write_paper(tmp_path, manifest)

    with pytest.raises(RestrictedPaperError):
        PaperStore(tmp_path).read_manifest(ARXIV)


def test_topic_lists_its_papers_and_a_shared_paper_appears_under_both(tmp_path: Path) -> None:
    first, second = "2610.23820", "2610.00001"
    _write_paper(tmp_path, _manifest(), arxiv_id=first)
    _write_paper(tmp_path, _manifest(arxiv_id=second), arxiv_id=second)
    _write_membership(
        tmp_path,
        [("alpha", first), ("beta", first), ("alpha", second)],
    )
    store = PaperStore(tmp_path)

    assert store.topic_papers("alpha") == [first, second]
    assert store.topic_papers("beta") == [first]
    assert store.topic_papers("gamma") == []


def test_membership_line_for_a_paper_without_a_directory_is_broken(tmp_path: Path) -> None:
    _write_membership(tmp_path, [("alpha", "2610.99999")])

    with pytest.raises(BrokenPaperError, match="no paper directory"):
        PaperStore(tmp_path).topic_papers("alpha")


def test_reader_module_does_not_import_tool_lit_review() -> None:
    tree = ast.parse(Path(paper_store.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert not {name for name in imported if name.split(".")[0] == "tool_lit_review"}
