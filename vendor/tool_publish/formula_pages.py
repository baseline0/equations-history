"""Formula record pages: the public view of formula-record/1, rendered as static HTML with KaTeX.

The input is plain JSON that the caller writes (the public view from equations-history). This module knows nothing
about where the records came from. It refuses any field the public view must not carry, so an internal file path or
source line cannot reach a page by accident.

Every build is a preview. The output carries BUILD.json with preview set, so assert_deployable refuses it. Publishing
is a separate, reviewed step.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

KATEX_VERSION = "0.16.11"
KATEX_BASE = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist"
# Passed to auto-render as JavaScript. Only \[ and \] are math delimiters, so stray dollar signs stay as text.
DISPLAY_DELIMITERS = "{delimiters: [{left: '\\\\[', right: '\\\\]', display: true}]}"
BUILD_RECORD = "BUILD.json"
RECORD_SUFFIX = ".json"
# Review sign-offs live beside the records, keyed by record id. Not a record, so the loader skips it.
REVIEWS_FILE = "reviews.json"

# Math markers that would show as stray text in a title. Formulas belong in core.latex, not in the name.
_MATH_MARKERS = ("_", "^", "\\", "$")
_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

# The public view's fields, and nothing else. Anything outside these sets is refused.
_ALLOWED: dict[str, Any] = {
    "id": None,
    "core": {"name", "latex", "units", "assumptions"},
    "provenance": {
        "code": {"repo"},
        "literature": {"paper_store_id", "version", "locator"},
    },
    "narrative": {"year", "history", "citations", "concepts"},
}
_REQUIRED = ("id", "core", "narrative")


class FormulaPageError(ValueError):
    """A record cannot be rendered. The message names the file and the problem."""


def check_public_record(record: Mapping[str, Any]) -> list[str]:
    """Every reason ``record`` is not a public formula record. An empty list means it can be rendered."""
    problems = [f"missing {name}" for name in _REQUIRED if name not in record]
    problems.extend(_unexpected(record, _ALLOWED, path="record"))
    if isinstance(record.get("id"), str) and not _ID.fullmatch(record["id"]):
        problems.append(f"id {record['id']!r} is not a lowercase slug")
    core = record.get("core")
    if isinstance(core, Mapping):
        units = core.get("units")
        if not (isinstance(units, Mapping) and {"lhs", "rhs"} <= units.keys()):
            problems.append("core.units needs lhs and rhs")
        if not isinstance(core.get("latex"), str) or not core["latex"].strip():
            problems.append("core.latex must be a non-empty string")
        name = core.get("name")
        if isinstance(name, str) and any(marker in name for marker in _MATH_MARKERS):
            problems.append("core.name is shown as plain text; put formulas in core.latex")
    return problems


def _unexpected(value: Mapping[str, Any], allowed: Mapping[str, Any], *, path: str) -> list[str]:
    """Keys in ``value`` that ``allowed`` does not name, recursing into the nested mappings it describes."""
    problems: list[str] = []
    for key, sub in value.items():
        if key not in allowed:
            problems.append(f"{path}.{key} is not part of the public view")
        elif isinstance(allowed[key], Mapping) and isinstance(sub, Mapping):
            problems.extend(_unexpected(sub, allowed[key], path=f"{path}.{key}"))
        elif isinstance(allowed[key], set) and isinstance(sub, Mapping):
            problems.extend(
                f"{path}.{key}.{field} is not part of the public view" for field in sub if field not in allowed[key]
            )
    return problems


def load_public_records_with_digests(records_dir: Path) -> list[tuple[dict[str, Any], str]]:
    """Every record in ``records_dir`` with the sha256 of its bytes, checked.

    Raises FormulaPageError on the first unreadable or invalid file. A duplicate id is refused too.
    """
    loaded: list[tuple[dict[str, Any], str]] = []
    seen: set[str] = set()
    for path in sorted(records_dir.glob(f"*{RECORD_SUFFIX}")):
        if path.name == REVIEWS_FILE:
            continue
        data = path.read_bytes()
        try:
            record = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise FormulaPageError(f"{path.name}: cannot read JSON: {error}") from error
        if not isinstance(record, dict):
            raise FormulaPageError(f"{path.name}: a formula record is a JSON object")
        problems = check_public_record(record)
        if problems:
            raise FormulaPageError(f"{path.name}: " + "; ".join(problems))
        if record["id"] in seen:
            raise FormulaPageError(f"{path.name}: duplicate id {record['id']!r}")
        seen.add(record["id"])
        loaded.append((record, hashlib.sha256(data).hexdigest()))
    if not loaded:
        raise FormulaPageError(f"{records_dir}: no formula records to render")
    return loaded


def load_public_records(records_dir: Path) -> list[dict[str, Any]]:
    """The records in ``records_dir``, checked. See load_public_records_with_digests."""
    return [record for record, _ in load_public_records_with_digests(records_dir)]


def load_reviews(path: Path) -> dict[str, dict[str, str]]:
    """The review sign-offs, keyed by record id. A missing file means no reviews yet."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FormulaPageError(f"{path.name}: cannot read JSON: {error}") from error
    if not isinstance(data, dict) or not all(isinstance(value, dict) for value in data.values()):
        raise FormulaPageError(f"{path.name}: expected an object of review objects keyed by record id")
    return data


def review_problems(digests: Mapping[str, str], reviews: Mapping[str, Mapping[str, str]]) -> list[str]:
    """Every record that lacks a current review. A review is current only while the record's bytes are unchanged."""
    problems: list[str] = []
    for record_id, digest in sorted(digests.items()):
        review = reviews.get(record_id)
        if review is None:
            problems.append(f"{record_id}: no review recorded")
        elif review.get("sha256") != digest:
            problems.append(f"{record_id}: the record changed since it was reviewed; review it again")
        elif not str(review.get("reviewed_by", "")).strip():
            problems.append(f"{record_id}: the review names no reviewer")
    return problems


def approve_record(records_dir: Path, reviews_path: Path, record_id: str, reviewer: str, *, now: datetime) -> None:
    """Record a review of one record, pinned to its current bytes. The record must exist in ``records_dir``."""
    if not reviewer.strip():
        raise FormulaPageError("a review needs a reviewer name")
    digests = {record["id"]: digest for record, digest in load_public_records_with_digests(records_dir)}
    if record_id not in digests:
        raise FormulaPageError(f"{record_id}: no such record in {records_dir}")
    reviews = load_reviews(reviews_path)
    reviews[record_id] = {"reviewed_by": reviewer, "reviewed_at": now.isoformat(), "sha256": digests[record_id]}
    reviews_path.write_text(json.dumps(dict(sorted(reviews.items())), indent=2) + "\n", encoding="utf-8")


class FormulaBuildMode(StrEnum):
    """A preview is always allowed. A deployable build needs a current review of every record it includes."""

    PREVIEW = "preview"
    DEPLOYABLE = "deployable"


def _escape_all(values: Any) -> list[str]:
    return [html.escape(str(value)) for value in values]


def _preview_line(preview: bool) -> str:
    return '<p class="units">Preview: not reviewed for publication.</p>' if preview else ""


def _robots(preview: bool) -> str:
    """Preview pages are kept out of search. Reviewed pages are public and indexable: the review gate decides what ships."""
    return '<meta name="robots" content="noindex">' if preview else ""


def render_formula_page(record: Mapping[str, Any], *, preview: bool = True) -> str:
    """One formula as a self-contained page. KaTeX is loaded from a pinned CDN release; the LaTeX is escaped first.

    The preview label appears only in a preview build. The default is the safe one: a caller that forgets to pass
    the mode gets a page marked as unreviewed.
    """
    core = record["core"]
    narrative = record["narrative"]
    provenance = record.get("provenance", {})
    literature = provenance.get("literature")
    literature_line = (
        f"<p>Literature: {html.escape(literature['paper_store_id'])} {html.escape(literature['version'])}, "
        f"{html.escape(literature['locator'])}.</p>"
        if literature
        else ""
    )
    assumptions = "".join(f"<li>{item}</li>" for item in _escape_all(core["assumptions"]))
    citations = "".join(f"<li>{item}</li>" for item in _escape_all(narrative["citations"]))
    concepts = ", ".join(_escape_all(narrative["concepts"]))
    year = "unknown" if narrative["year"] is None else str(narrative["year"])
    name = html.escape(core["name"])
    lhs = html.escape(core["units"]["lhs"])
    rhs = html.escape(core["units"]["rhs"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{_robots(preview)}
<title>{name}</title>
<link rel="stylesheet" href="{KATEX_BASE}/katex.min.css">
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 42rem; margin: 0 auto; padding: 1rem; line-height: 1.5; }}
  .equation {{ overflow-x: auto; padding: 0.5rem 0; }}
  .units {{ color: #555; font-size: 0.95rem; }}
</style>
</head>
<body>
<main>
<h1>{name}</h1>
{_preview_line(preview)}
<div class="equation">\\[{html.escape(core["latex"])}\\]</div>
<p class="units">Units: left-hand side {lhs}; right-hand side {rhs}.</p>
<h2>Assumptions</h2>
<ul>{assumptions}</ul>
<h2>History</h2>
<p>{html.escape(narrative["history"])}</p>
<p>First published: {year}.</p>
<h2>Citations</h2>
<ul>{citations}</ul>
<p>Concepts: {concepts}.</p>
<p>Source: {html.escape(provenance.get("code", {}).get("repo", "not recorded"))}.</p>
{literature_line}
</main>
<script src="{KATEX_BASE}/katex.min.js"></script>
<script src="{KATEX_BASE}/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {DISPLAY_DELIMITERS})"></script>
</body>
</html>
"""


def render_index(records: list[Mapping[str, Any]], *, preview: bool = True) -> str:
    """The index page: one link per record, in the order given. The preview label appears only in a preview build."""
    items = "".join(
        f'<li><a href="{html.escape(record["id"])}/">{html.escape(record["core"]["name"])}</a></li>'
        for record in records
    )
    title = "Formula records (preview)" if preview else "Formula records"
    note = "<p>Not reviewed for publication.</p>" if preview else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{_robots(preview)}
<title>{title}</title>
</head>
<body>
<main>
<h1>{title}</h1>
{note}
<ul>{items}</ul>
</main>
</body>
</html>
"""


def build_formula_pages(
    records_dir: Path,
    out: Path,
    *,
    mode: FormulaBuildMode,
    reviews_path: Path,
    now: datetime,
) -> Path:
    """Write one page per record, an index, and a BUILD.json that says whether the build is a preview.

    A deployable build refuses any record without a current review. Nothing is written when a check fails.
    """
    loaded = load_public_records_with_digests(records_dir)
    if mode is FormulaBuildMode.DEPLOYABLE:
        problems = review_problems({record["id"]: digest for record, digest in loaded}, load_reviews(reviews_path))
        if problems:
            raise FormulaPageError("not deployable: " + "; ".join(problems))
    records = [record for record, _ in loaded]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    preview = mode is FormulaBuildMode.PREVIEW
    for record in records:
        page = out / record["id"]
        page.mkdir()
        (page / "index.html").write_text(render_formula_page(record, preview=preview), encoding="utf-8")
    (out / "index.html").write_text(render_index(records, preview=preview), encoding="utf-8")
    build = {
        "site": "formula-records",
        "built_at": now.isoformat(),
        "preview": preview,
        "records": [record["id"] for record in records],
        "katex": KATEX_VERSION,
    }
    (out / BUILD_RECORD).write_text(json.dumps(build, indent=2) + "\n", encoding="utf-8")
    return out
