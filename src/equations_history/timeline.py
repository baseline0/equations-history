"""Timeline of collected equations for chosen papers, read from tool-lit-review's knowledge export.

Design Intent:
- Reads only. The input is the snapshot file named by the knowledge-export contract
  (fleet-coordination/contracts/knowledge-export/FORMAT.md). This module never imports tool-lit-review.
- Only items of kind ``formula`` are read. Their LaTeX is the source's own text, so it is compared, never rewritten.
- Two formulas are the same equation only when their LaTeX is equal after normalisation: labels, display delimiters and
  whitespace removed. This is a deliberate, narrow rule. A different notation for the same equation is a different
  entry, and the report says so rather than merging it.
- Items whose paper has no recorded publication date go in an explicit "unknown date" bucket, after every dated entry.
  They are never placed by guessing a date.
"""

from __future__ import annotations

import json
import re
from collections.abc import Collection
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA_KIND = "formula"
_LABEL = re.compile(r"\\label\{[^{}]*\}")
_ENV_DELIMITERS = re.compile(
    r"\\(?:begin|end)\{(?:equation|align|gather|multline|eqnarray|displaymath)\*?\}|\\\[|\\\]|\$\$"
)


class ExportError(ValueError):
    """The knowledge export is not in the shape the contract describes."""


@dataclass(frozen=True)
class Occurrence:
    """One paper in which an equation is collected, with where and when."""

    paper_id: str
    locator: str
    published: date | None
    item_id: str


@dataclass(frozen=True)
class TimelineEntry:
    """One distinct equation and every chosen paper that states it."""

    latex: str
    key: str
    first_seen: date | None
    occurrences: tuple[Occurrence, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Timeline:
    """Dated entries in publication order, then the entries whose papers have no date."""

    dated: tuple[TimelineEntry, ...]
    unknown_date: tuple[TimelineEntry, ...]


def normalise_latex(latex: str) -> str:
    """A comparison key: labels, display delimiters and whitespace removed. Two equal keys are the same equation."""
    text = _LABEL.sub("", latex)
    text = _ENV_DELIMITERS.sub("", text)
    return re.sub(r"\s+", "", text)


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as error:
        raise ExportError(f"paper_published must be YYYY-MM-DD or null, got {value!r}") from error


def load_formulas(path: Path) -> list[tuple[dict[str, Any], date | None]]:
    """The formula items in a knowledge export, each with its paper's publication date. Malformed items are refused."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "items" not in payload or not isinstance(payload["items"], list):
        raise ExportError("the export has no items list; expected the knowledge-export contract")
    rows = []
    for item in payload["items"]:
        if item.get("kind") != SCHEMA_KIND:
            continue
        for required in ("id", "latex", "source", "paper_published"):
            if required not in item:
                raise ExportError(f"formula {item.get('id')!r} is missing {required!r}")
        source = item["source"]
        if not source.get("paper_id") or not source.get("locator"):
            raise ExportError(f"formula {item['id']!r} has no paper_id or locator")
        if not str(item["latex"]).strip():
            raise ExportError(f"formula {item['id']!r} has empty LaTeX")
        rows.append((item, _parse_date(item["paper_published"])))
    return rows


def build_timeline(export: Path, papers: Collection[str]) -> Timeline:
    """Entries for the chosen papers, grouped by equation. Empty ``papers`` is refused, so nothing is silently everything."""
    if not papers:
        raise ValueError("choose at least one paper; a timeline of every paper is not built by default")
    groups: dict[str, list[tuple[str, str, Occurrence]]] = {}
    for item, published in load_formulas(export):
        if item["source"]["paper_id"] not in papers:
            continue
        occurrence = Occurrence(
            paper_id=item["source"]["paper_id"],
            locator=item["source"]["locator"],
            published=published,
            item_id=item["id"],
        )
        groups.setdefault(normalise_latex(item["latex"]), []).append((item["id"], item["latex"], occurrence))

    entries = []
    for key, members in groups.items():
        occurrences = tuple(
            sorted((m[2] for m in members), key=lambda o: (o.published is None, o.published or date.min, o.paper_id))
        )
        dates = [o.published for o in occurrences if o.published is not None]
        entries.append(
            TimelineEntry(
                latex=members[0][1],
                key=key,
                first_seen=min(dates) if dates else None,
                occurrences=occurrences,
            )
        )
    dated = sorted((e for e in entries if e.first_seen is not None), key=lambda e: (e.first_seen, e.key))
    unknown = sorted((e for e in entries if e.first_seen is None), key=lambda e: e.key)
    return Timeline(dated=tuple(dated), unknown_date=tuple(unknown))


def render(timeline: Timeline) -> str:
    """Plain text: one block per equation, dated blocks first, then the unknown-date bucket."""
    lines: list[str] = []
    for entry in timeline.dated:
        if entry.first_seen is None:
            raise ValueError("a dated entry has no date; build_timeline puts undated entries in unknown_date")
        lines.append(f"{entry.first_seen.isoformat()}  {entry.latex.strip()}")
        for occurrence in entry.occurrences:
            lines.append(
                f"    {occurrence.published.isoformat() if occurrence.published else 'unknown'}  {occurrence.paper_id}  ({occurrence.locator})"
            )
    if timeline.unknown_date:
        lines.append("unknown date")
        for entry in timeline.unknown_date:
            lines.append(f"  {entry.latex.strip()}")
            for occurrence in entry.occurrences:
                lines.append(f"    {occurrence.paper_id}  ({occurrence.locator})")
    if not lines:
        lines.append("no collected formulas in the chosen papers")
    return "\n".join(lines)


def as_json(timeline: Timeline) -> dict[str, Any]:
    def entry_dict(entry: TimelineEntry) -> dict[str, Any]:
        return {
            "latex": entry.latex,
            "first_seen": entry.first_seen.isoformat() if entry.first_seen else None,
            "occurrences": [
                {
                    "paper_id": o.paper_id,
                    "published": o.published.isoformat() if o.published else None,
                    "locator": o.locator,
                    "item_id": o.item_id,
                }
                for o in entry.occurrences
            ],
        }

    return {
        "dated": [entry_dict(e) for e in timeline.dated],
        "unknown_date": [entry_dict(e) for e in timeline.unknown_date],
    }
