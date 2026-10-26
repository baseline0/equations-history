"""Timeline of collected equations: grouping, dating, the unknown-date bucket, refusals, and the CLI. Offline."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from equations_history import cli
from equations_history.timeline import ExportError, Timeline, TimelineEntry, build_timeline, normalise_latex, render

pytestmark = pytest.mark.unit

OLD = "2401.00001v1"
NEW = "2609.16108v1"
UNDATED = "2612.00009v1"
GKSL = "\\begin{align}\n\\label{eq:gksl}\n  \\dot{\\rho} = -i[H,\\rho]\n\\end{align}"
GKSL_BARE = "\\dot{\\rho} = -i[H,\\rho]"


def _item(item_id: str, latex: str, paper: str, published: str | None, locator: str = "s1") -> dict[str, Any]:
    return {
        "id": item_id,
        "kind": "formula",
        "latex": latex,
        "source": {"paper_id": paper, "locator": locator, "quote": latex, "origin": "tex-source"},
        "paper_published": published,
    }


@pytest.fixture
def export(tmp_path: Path) -> Path:
    items = [
        _item("formula-gksl", GKSL, NEW, "2026-09-14"),
        _item("formula-gksl-old", GKSL_BARE, OLD, "2024-01-05", "s3"),
        _item("formula-undated", "E = mc^2", UNDATED, None),
        _item("formula-other", "a = b", NEW, "2026-09-14", "s9"),
        {"id": "fact-x", "kind": "fact", "value": "1", "source": {"paper_id": NEW}, "paper_published": "2026-09-14"},
    ]
    path = tmp_path / "collected.json"
    path.write_text(json.dumps({"counts": {}, "items": items}), encoding="utf-8")
    return path


def test_the_same_equation_in_two_papers_is_one_entry_dated_by_its_earliest_paper(export: Path) -> None:
    result = build_timeline(export, {OLD, NEW})

    gksl = [e for e in result.dated if normalise_latex(e.latex) == normalise_latex(GKSL_BARE)]
    assert len(gksl) == 1
    assert gksl[0].first_seen == date(2024, 1, 5)
    assert [o.paper_id for o in gksl[0].occurrences] == [OLD, NEW]


def test_dated_entries_come_in_publication_order(export: Path) -> None:
    result = build_timeline(export, {OLD, NEW})

    assert [e.first_seen for e in result.dated] == [date(2024, 1, 5), date(2026, 9, 14)]


def test_an_undated_paper_goes_in_the_unknown_bucket_after_every_dated_entry(export: Path) -> None:
    result = build_timeline(export, {OLD, NEW, UNDATED})

    assert result.unknown_date and result.unknown_date[0].occurrences[0].paper_id == UNDATED
    assert result.unknown_date[0].first_seen is None
    assert "unknown date" in render(result)


def test_only_the_chosen_papers_are_considered(export: Path) -> None:
    result = build_timeline(export, {NEW})

    assert {o.paper_id for e in result.dated for o in e.occurrences} == {NEW}
    assert result.unknown_date == ()


def test_labels_and_display_delimiters_do_not_separate_equal_equations() -> None:
    assert normalise_latex(GKSL) == normalise_latex(GKSL_BARE)


def test_different_notation_for_the_same_idea_stays_as_two_entries(tmp_path: Path) -> None:
    path = tmp_path / "collected.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    _item("formula-a", "\\frac{a}{b}", NEW, "2026-09-14"),
                    _item("formula-b", "a/b", OLD, "2024-01-05"),
                ]
            }
        ),
        encoding="utf-8",
    )

    result = build_timeline(path, {NEW, OLD})

    assert len(result.dated) == 2


def test_a_choice_of_no_papers_is_refused_rather_than_meaning_everything(export: Path) -> None:
    with pytest.raises(ValueError, match="choose at least one paper"):
        build_timeline(export, set())


def test_a_formula_without_its_publication_field_is_refused(tmp_path: Path) -> None:
    broken = _item("formula-broken", "x", NEW, "2026-09-14")
    del broken["paper_published"]
    path = tmp_path / "collected.json"
    path.write_text(json.dumps({"items": [broken]}), encoding="utf-8")

    with pytest.raises(ExportError, match="paper_published"):
        build_timeline(path, {NEW})


def test_a_publication_date_that_is_not_a_date_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "collected.json"
    path.write_text(json.dumps({"items": [_item("formula-bad", "x", NEW, "last tuesday")]}), encoding="utf-8")

    with pytest.raises(ExportError, match="YYYY-MM-DD"):
        build_timeline(path, {NEW})


def test_a_file_that_is_not_an_export_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "other.json"
    path.write_text(json.dumps({"rows": []}), encoding="utf-8")

    with pytest.raises(ExportError, match="no items list"):
        build_timeline(path, {NEW})


def test_the_cli_prints_the_timeline_and_exits_2_on_a_bad_export(export: Path, tmp_path: Path) -> None:
    runner = CliRunner()

    ok = runner.invoke(cli.app, ["timeline", "--export", str(export), "--paper", f"{OLD},{NEW}"])
    assert ok.exit_code == 0
    assert "2024-01-05" in ok.output

    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    refused = runner.invoke(cli.app, ["timeline", "--export", str(bad), "--paper", NEW])
    assert refused.exit_code == 2


def test_the_cli_json_output_has_dated_and_unknown_sections(export: Path) -> None:
    result = CliRunner().invoke(cli.app, ["timeline", "--export", str(export), "--paper", f"{OLD},{UNDATED}", "--json"])

    payload = json.loads(result.output)
    assert payload["dated"][0]["first_seen"] == "2024-01-05"
    assert payload["unknown_date"][0]["occurrences"][0]["paper_id"] == UNDATED


def test_render_refuses_a_dated_entry_without_a_date() -> None:
    """build_timeline never puts an undated entry in the dated list. A hand-built one is refused, not printed as None."""
    broken = Timeline(dated=(TimelineEntry(latex="x", key="x", first_seen=None, occurrences=()),), unknown_date=())

    with pytest.raises(ValueError, match="unknown_date"):
        render(broken)
