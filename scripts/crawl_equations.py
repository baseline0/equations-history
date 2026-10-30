"""Crawl arXiv papers' TeX source into the equation catalog, and report the parse rate.

Usage (from the repo root):
    uv run python scripts/crawl_equations.py --ids-file PATH --cache-dir DIR --catalog FILE --report FILE

--ids-file is a text file with one arXiv identifier per line (e.g. 2610.28611v1). Blank lines and lines starting with
# are ignored. Every path is an argument, so nothing is assumed about where the run writes. The run prints the aggregate
counts and writes the JSON report. Fetching is paced at one request per second, and cached bundles make no request.
"""

from __future__ import annotations

from pathlib import Path

import typer

from equations_history import crawl

app = typer.Typer(add_completion=False, help="Crawl arXiv TeX sources into the equation catalog.")


def read_ids(path: Path) -> list[str]:
    """The identifiers in an ids file: one per line, with blank lines and # comments skipped."""
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]


@app.command()
def main(
    ids_file: Path = typer.Option(..., "--ids-file", exists=True, dir_okay=False, help="One arXiv ID per line."),
    cache_dir: Path = typer.Option(..., "--cache-dir", help="Directory where raw e-print bundles are cached."),
    catalog: Path = typer.Option(..., "--catalog", help="Equation catalog (JSON Lines) to write."),
    report: Path = typer.Option(..., "--report", help="JSON report with per-paper counts to write."),
) -> None:
    """Fetch, extract and parse every listed paper, then write the catalog and the report."""
    ids = read_ids(ids_file)
    result = crawl.crawl(ids, cache_dir, crawl.http_fetch, crawl.Pacer())
    written = crawl.write_catalog(catalog, result.records)
    payload = crawl.write_report(report, result, paper_list=str(ids_file))
    totals = payload["totals"]
    rate = totals["parse_rate"]
    typer.echo(
        f"papers listed {totals['papers_listed']}, ok {totals['papers_ok']}; "
        f"equations found {totals['equations_found']}, parsed {totals['equations_parsed']}, "
        f"parse rate {'n/a' if rate is None else f'{rate:.1%}'}; catalog records {written}"
    )
    for reason, count in list(totals["failure_reasons"].items())[:5]:
        typer.echo(f"  {count:4d}  {reason}")


if __name__ == "__main__":
    app()
