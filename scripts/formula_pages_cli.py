"""Build the formula pages and record reviews, using the vendored renderer in vendor/tool_publish.

The records and their review sign-offs live in formula-records/, and this repo publishes them, so it also owns the
approvals. A deployable build needs a current review of every record; a preview is marked and must not be published.

    uv run python scripts/formula_pages_cli.py build --mode deployable --out pages
    uv run python scripts/formula_pages_cli.py approve --id michaelis-menten --reviewer "Name"
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

import typer

from equations_history.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "vendor" / "tool_publish"))
import formula_pages

RECORDS = REPO_ROOT / "formula-records"
REVIEWS = RECORDS / "reviews.json"

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def build(
    mode: str = typer.Option(..., "--mode", help="deployable (every record needs a current review) or preview."),
    out: Path = typer.Option(..., "--out", help="Where to write the pages."),
) -> None:
    """Render the records as pages. A refused build writes nothing."""
    try:
        written = formula_pages.build_formula_pages(
            RECORDS,
            out,
            mode=formula_pages.FormulaBuildMode(mode),
            reviews_path=REVIEWS,
            now=datetime.now(UTC),
        )
    except formula_pages.FormulaPageError as error:
        typer.echo(f"build refused: {error}")
        raise typer.Exit(1) from error
    typer.echo(f"built {written} ({mode})")


@app.command()
def approve(
    record_id: str = typer.Option(..., "--id", help="The record to approve, for example michaelis-menten."),
    reviewer: str = typer.Option(..., "--reviewer", help="The person who reviewed the record, by name."),
) -> None:
    """Record that a person reviewed one record. The review is pinned to the record's bytes, so an edit voids it."""
    try:
        formula_pages.approve_record(RECORDS, REVIEWS, record_id, reviewer, now=datetime.now(UTC))
    except formula_pages.FormulaPageError as error:
        typer.echo(f"approval refused: {error}")
        raise typer.Exit(1) from error
    typer.echo(f"approved {record_id} by {reviewer}")


@app.command("approve-all")
def approve_all(
    reviewer: str = typer.Option(..., "--reviewer", help="The person who reviewed every record, by name."),
) -> None:
    """Record one review for each record in formula-records/, each pinned to its current bytes.

    Run it only after reading the change to formula-records/ (git diff). Every record is approved; none is skipped.
    """
    try:
        records = formula_pages.load_public_records_with_digests(RECORDS)
        for record, _ in records:
            formula_pages.approve_record(RECORDS, REVIEWS, record["id"], reviewer, now=datetime.now(UTC))
    except formula_pages.FormulaPageError as error:
        typer.echo(f"approval refused: {error}")
        raise typer.Exit(1) from error
    typer.echo(f"approved {len(records)} record(s) by {reviewer}: {', '.join(r['id'] for r, _ in records)}")


if __name__ == "__main__":
    app()
