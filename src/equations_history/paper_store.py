"""Read the paper store v1 from a root directory the caller supplies.

The format is defined in fleet-coordination/contracts/paper-store/FORMAT.md, and this module follows it exactly. It
never imports tool_lit_review: the on-disk layout is the only interface. The licence rule is applied again here, as
the contract requires, so a manifest that the writer's gate let through is still refused on read.

Reads only. Writers own put_blob and set_latest; a reader never writes to the store.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1
LATEST_NAME = "latest"
MANIFEST_SUFFIX = ".json"
MEMBERSHIP_PATH = Path("catalog") / "membership.jsonl"

# Canonical licence URLs the contract allows a reader to treat as open. Exact match only: the contract names
# canonical URLs, so http:// or a trailing slash is refused rather than normalised.
ALLOWED_LICENCES: frozenset[str] = frozenset(
    {
        "https://creativecommons.org/licenses/by/4.0",
        "https://creativecommons.org/licenses/by-sa/4.0",
        "https://creativecommons.org/publicdomain/zero/1.0",
    }
)
STATUSES: frozenset[str] = frozenset({"saved", "cached", "skipped", "failed"})

# arXiv IDs as the contract writes them: YYMM.NNNN or YYMM.NNNNN, with no version suffix.
_ARXIV_ID = re.compile(r"\d{4}\.\d{4,5}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_MANIFEST_FIELDS: tuple[str, ...] = (
    "schema_version",
    "arxiv_id",
    "version",
    "title",
    "doi",
    "licence",
    "pdf_sha256",
    "tex_sha256",
    "status",
    "fetched_at",
)
_MEMBERSHIP_FIELDS: tuple[str, ...] = ("topic", "arxiv_id", "query", "added_at")


class PaperStoreError(ValueError):
    """Base class for every refusal the paper store reader raises."""


class PaperNotFoundError(PaperStoreError):
    """No paper directory, or no `latest` pointer, exists for the requested arXiv ID."""


class BrokenPaperError(PaperStoreError):
    """A manifest, pointer, membership line or blob is missing or inconsistent. The reader does not guess."""


class RestrictedPaperError(PaperStoreError):
    """The manifest's licence is not one of the canonical open licences, so the paper is refused."""


@dataclass(frozen=True, slots=True)
class Manifest:
    """One immutable manifest, `papers/<arxiv-id>/<version>.json`, with every field the contract lists."""

    schema_version: int
    arxiv_id: str
    version: str
    title: str
    doi: str | None
    licence: str
    pdf_sha256: str | None
    tex_sha256: str | None
    status: str
    fetched_at: str


@dataclass(frozen=True, slots=True)
class PaperRecord:
    """A paper's manifest, plus the TeX bundle bytes when the manifest names one."""

    manifest: Manifest
    tex: bytes | None


def _check_licence(licence: object, source: Path) -> None:
    """Refuse any licence that is not an allowed canonical URL, including a missing or non-string one."""
    if not isinstance(licence, str) or licence not in ALLOWED_LICENCES:
        raise RestrictedPaperError(
            f"{source}: licence {licence!r} is restricted; only {', '.join(sorted(ALLOWED_LICENCES))} may be read"
        )


def _parse_manifest(data: dict[str, Any], *, arxiv_id: str, source: Path) -> Manifest:
    """Check every field the contract lists, and return them as a Manifest, or raise BrokenPaperError."""

    def broken(problem: str) -> BrokenPaperError:
        return BrokenPaperError(f"{source}: {problem}")

    missing = [name for name in _MANIFEST_FIELDS if name not in data]
    if missing:
        raise broken(f"missing field(s) {', '.join(missing)}")

    schema_version = data["schema_version"]
    if type(schema_version) is not int or schema_version != SCHEMA_VERSION:
        raise broken(f"schema_version must be {SCHEMA_VERSION}, got {schema_version!r}")
    if data["arxiv_id"] != arxiv_id:
        raise broken(f"arxiv_id {data['arxiv_id']!r} does not match directory {arxiv_id!r}")
    for name in ("version", "title", "licence", "fetched_at"):
        if not isinstance(data[name], str) or not data[name]:
            raise broken(f"{name} must be a non-empty string")
    if data["doi"] is not None and not isinstance(data["doi"], str):
        raise broken("doi must be a string or null")
    for name in ("pdf_sha256", "tex_sha256"):
        value = data[name]
        if value is not None and not (isinstance(value, str) and _SHA256.fullmatch(value)):
            raise broken(f"{name} must be a lowercase sha256 hex string or null")
    if data["status"] not in STATUSES:
        raise broken(f"status {data['status']!r} is not one of {', '.join(sorted(STATUSES))}")
    try:
        fetched = datetime.fromisoformat(data["fetched_at"])
    except ValueError as exc:
        raise broken(f"fetched_at {data['fetched_at']!r} is not ISO 8601") from exc
    if fetched.tzinfo is None:
        raise broken("fetched_at must carry a UTC offset")

    return Manifest(
        schema_version=schema_version,
        arxiv_id=arxiv_id,
        version=data["version"],
        title=data["title"],
        doi=data["doi"],
        licence=data["licence"],
        pdf_sha256=data["pdf_sha256"],
        tex_sha256=data["tex_sha256"],
        status=data["status"],
        fetched_at=data["fetched_at"],
    )


def _parse_membership_row(line: str, *, source: Path, number: int) -> dict[str, str]:
    """Parse one membership line: a JSON object with the four string fields the contract lists."""
    try:
        row = json.loads(line)
    except json.JSONDecodeError as exc:
        raise BrokenPaperError(f"{source}:{number}: line is not JSON ({exc})") from exc
    if not isinstance(row, dict):
        raise BrokenPaperError(f"{source}:{number}: line must be a JSON object")
    for name in _MEMBERSHIP_FIELDS:
        if not isinstance(row.get(name), str) or not row[name]:
            raise BrokenPaperError(f"{source}:{number}: field {name!r} must be a non-empty string")
    if not _ARXIV_ID.fullmatch(row["arxiv_id"]):
        raise BrokenPaperError(f"{source}:{number}: arxiv_id {row['arxiv_id']!r} is not an arXiv ID")
    return {name: row[name] for name in _MEMBERSHIP_FIELDS}


class PaperStore:
    """A paper store at a root the caller chose. Nothing here assumes a location."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def blob_path(self, sha256: str) -> Path:
        """Return where a blob lives, `blobs/<sha[0:2]>/<sha>`, after checking the name is a sha256."""
        if not _SHA256.fullmatch(sha256):
            raise BrokenPaperError(f"{sha256!r} is not a lowercase sha256 hex string")
        return self.root / "blobs" / sha256[:2] / sha256

    def get_blob(self, sha256: str) -> bytes:
        """Return the blob's bytes. Refuses when it is absent or does not hash to its own name."""
        path = self.blob_path(sha256)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise BrokenPaperError(f"blob {sha256} is missing: {path}") from exc
        if hashlib.sha256(data).hexdigest() != sha256:
            raise BrokenPaperError(f"blob {path} does not hash to its name {sha256}")
        return data

    def _paper_dir(self, arxiv_id: str) -> Path:
        if not _ARXIV_ID.fullmatch(arxiv_id):
            raise PaperStoreError(f"{arxiv_id!r} is not an arXiv ID without a version suffix")
        paper_dir = self.root / "papers" / arxiv_id
        if not paper_dir.is_dir():
            raise PaperNotFoundError(f"{arxiv_id}: no paper directory at {paper_dir}")
        return paper_dir

    def read_manifest(self, arxiv_id: str) -> Manifest:
        """Read `papers/<arxiv-id>/latest`, then the manifest it names, and apply the licence rule."""
        paper_dir = self._paper_dir(arxiv_id)
        latest = paper_dir / LATEST_NAME
        try:
            name = latest.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise PaperNotFoundError(f"{arxiv_id}: no latest pointer at {latest}") from exc

        stem = name.removesuffix(MANIFEST_SUFFIX)
        if PurePosixPath(name).name != name or not stem or stem == name:
            raise BrokenPaperError(f"{latest}: must name a manifest file in the same directory, got {name!r}")
        manifest_path = paper_dir / name
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise BrokenPaperError(f"{latest} names {name}, which is missing") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise BrokenPaperError(f"{manifest_path}: manifest is not readable JSON ({exc})") from exc
        if not isinstance(data, dict):
            raise BrokenPaperError(f"{manifest_path}: manifest must be a JSON object")

        # The licence gate runs before the other checks, so a restricted paper is refused whatever else it holds.
        _check_licence(data.get("licence"), manifest_path)
        manifest = _parse_manifest(data, arxiv_id=arxiv_id, source=manifest_path)
        if name != f"{manifest.version}{MANIFEST_SUFFIX}":
            raise BrokenPaperError(f"{manifest_path}: version {manifest.version!r} does not match its file name")
        return manifest

    def read_paper(self, arxiv_id: str) -> PaperRecord:
        """Return the paper's manifest and TeX bytes. A manifest whose named blob is missing is broken."""
        manifest = self.read_manifest(arxiv_id)
        if manifest.pdf_sha256 is not None and not self.blob_path(manifest.pdf_sha256).is_file():
            raise BrokenPaperError(f"{arxiv_id}: manifest names pdf blob {manifest.pdf_sha256}, which is missing")
        tex = self.get_blob(manifest.tex_sha256) if manifest.tex_sha256 is not None else None
        return PaperRecord(manifest=manifest, tex=tex)

    def topic_papers(self, topic: str) -> list[str]:
        """Return the arXiv IDs listed under a topic, in file order. A paper may belong to any number of topics.

        Every membership line is parsed, so a malformed line anywhere makes the file broken. A line for a topic
        must name a paper with a directory in the store, or the topic is broken.
        """
        if not topic:
            raise PaperStoreError("topic must be a non-empty string")
        membership = self.root / MEMBERSHIP_PATH
        try:
            lines = membership.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []

        papers: dict[str, None] = {}
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            row = _parse_membership_row(line, source=membership, number=number)
            if row["topic"] != topic:
                continue
            if not (self.root / "papers" / row["arxiv_id"]).is_dir():
                raise BrokenPaperError(
                    f"{membership}:{number}: topic {topic!r} names {row['arxiv_id']}, which has no paper directory"
                )
            papers[row["arxiv_id"]] = None
        return list(papers)
