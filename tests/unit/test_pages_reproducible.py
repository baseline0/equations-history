"""The published pages are exactly a deployable build of the reviewed records, so they cannot drift from their approvals.

Built into a temporary folder with the vendored renderer, then compared file by file with pages/. BUILD.json is compared
without its timestamp, which is the only field that changes between builds.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from equations_history.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "vendor" / "tool_publish"))
import formula_pages

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def test_the_published_pages_are_a_deployable_build_of_the_reviewed_records(tmp_path: Path) -> None:
    built = tmp_path / "pages"
    formula_pages.build_formula_pages(
        REPO_ROOT / "formula-records",
        built,
        mode=formula_pages.FormulaBuildMode.DEPLOYABLE,
        reviews_path=REPO_ROOT / "formula-records" / "reviews.json",
        now=NOW,
    )
    published = REPO_ROOT / "pages"

    assert _files(built) == _files(published)
    for rel in _files(built):
        if rel.name == "BUILD.json":
            fresh, shipped = (json.loads((root / rel).read_text(encoding="utf-8")) for root in (built, published))
            fresh.pop("built_at")
            shipped.pop("built_at")
            assert fresh == shipped, rel
        else:
            assert (built / rel).read_bytes() == (published / rel).read_bytes(), rel


def test_approve_all_reviews_every_record_against_its_current_bytes(tmp_path: Path) -> None:
    import shutil

    from typer.testing import CliRunner

    records = tmp_path / "formula-records"
    shutil.copytree(REPO_ROOT / "formula-records", records)
    for record in records.glob("*.json"):
        if record.name != "reviews.json":
            record.write_text(
                record.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )  # a changed byte voids the review
    import importlib.util

    spec = importlib.util.spec_from_file_location("formula_pages_cli", REPO_ROOT / "scripts" / "formula_pages_cli.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)

    original = cli.RECORDS, cli.REVIEWS
    cli.RECORDS, cli.REVIEWS = records, records / "reviews.json"
    try:
        result = CliRunner().invoke(cli.app, ["approve-all", "--reviewer", "Test"])
    finally:
        cli.RECORDS, cli.REVIEWS = original
    assert result.exit_code == 0, result.output
    digests = {r["id"]: d for r, d in formula_pages.load_public_records_with_digests(records)}
    assert formula_pages.review_problems(digests, formula_pages.load_reviews(records / "reviews.json")) == []
