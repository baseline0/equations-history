"""Tests for the arXiv crawler: bundle reading, pacing, fetch retry and caching, catalog and report writing, parse rate.

Offline: the HTTP function is a fake, the pacer's clock and sleep are fakes, and bundles are built in tmp_path.
"""

from __future__ import annotations

import gzip
import io
import json
import tarfile
from pathlib import Path
from typing import Any

import pytest

from equations_history import crawl
from equations_history.constants import REPO_ROOT

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "tex_equations" / "sample_paper.tex"
PAPER = "2610.00001v1"


def _tar_gz(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class FakeClock:
    """A clock that only moves when the test sleeps, so pacing is observable without real waits."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class ScriptedFetch:
    """Returns scripted responses in order: a (status, body) tuple, or an exception instance to raise."""

    def __init__(self, *responses: Any) -> None:
        self.responses = list(responses)
        self.urls: list[str] = []

    def __call__(self, url: str, timeout: float) -> tuple[int, bytes]:
        assert timeout == crawl.TIMEOUT_SECONDS
        self.urls.append(url)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def _pacer(clock: FakeClock) -> crawl.Pacer:
    return crawl.Pacer(interval=1.0, clock=clock.clock, sleep=clock.sleep)


def test_pacer_spaces_calls_one_second_apart() -> None:
    clock = FakeClock()
    pacer = _pacer(clock)
    for _ in range(3):
        pacer.wait()
    assert clock.sleeps == [1.0, 1.0]


def test_pacer_does_not_sleep_when_enough_time_has_passed() -> None:
    clock = FakeClock()
    pacer = _pacer(clock)
    pacer.wait()
    clock.now += 5.0
    pacer.wait()
    assert clock.sleeps == []


def test_tex_sources_reads_tex_members_of_a_tar_gz_bundle() -> None:
    bundle = _tar_gz(
        {"main.tex": b"\\begin{document}x\\end{document}", "fig.pdf": b"%PDF", "sec/intro.tex": b"\\section{A}"}
    )
    assert crawl.tex_sources(bundle) == {
        "main.tex": "\\begin{document}x\\end{document}",
        "sec/intro.tex": "\\section{A}",
    }


def test_tex_sources_reads_a_single_gzipped_tex_file() -> None:
    bundle = gzip.compress(b"\\documentclass{article}\\begin{document}\\[ x \\]\\end{document}")
    assert crawl.tex_sources(bundle) == {
        "main.tex": "\\documentclass{article}\\begin{document}\\[ x \\]\\end{document}"
    }


def test_tex_sources_refuses_a_non_tex_payload() -> None:
    with pytest.raises(crawl.BundleError):
        crawl.tex_sources(gzip.compress(b"just words, nothing else"))


def test_cache_hit_makes_no_request(tmp_path: Path) -> None:
    (tmp_path / f"{PAPER}.bundle").write_bytes(b"cached")
    fetch = ScriptedFetch()
    assert crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(FakeClock())) == b"cached"
    assert fetch.urls == []


def test_successful_fetch_is_cached(tmp_path: Path) -> None:
    fetch = ScriptedFetch((200, b"bundle-bytes"))
    assert crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(FakeClock())) == b"bundle-bytes"
    assert fetch.urls == [crawl.EPRINT_URL.format(paper_id=PAPER)]
    assert (tmp_path / f"{PAPER}.bundle").read_bytes() == b"bundle-bytes"


def test_network_error_is_retried_once_then_succeeds(tmp_path: Path) -> None:
    clock = FakeClock()
    fetch = ScriptedFetch(TimeoutError("slow"), (200, b"ok"))
    assert crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(clock)) == b"ok"
    assert len(fetch.urls) == 2
    assert clock.sleeps == [1.0]


def test_two_network_errors_fail_with_the_reason(tmp_path: Path) -> None:
    fetch = ScriptedFetch(TimeoutError("slow"), TimeoutError("slow"))
    with pytest.raises(crawl.FetchFailed, match="network error"):
        crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(FakeClock()))
    assert len(fetch.urls) == 2


def test_client_error_is_not_retried(tmp_path: Path) -> None:
    fetch = ScriptedFetch((404, b""))
    with pytest.raises(crawl.FetchFailed, match="HTTP 404"):
        crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(FakeClock()))
    assert len(fetch.urls) == 1


def test_rate_limit_raises_and_is_not_retried(tmp_path: Path) -> None:
    fetch = ScriptedFetch((429, b""))
    with pytest.raises(crawl.RateLimited):
        crawl.fetch_bundle(PAPER, tmp_path, fetch, _pacer(FakeClock()))
    assert len(fetch.urls) == 1


def test_rate_limit_stops_the_run_and_lists_the_rest_as_not_attempted(tmp_path: Path) -> None:
    bundle = _tar_gz({"main.tex": FIXTURE.read_bytes()})
    (tmp_path / "2610.00001v1.bundle").write_bytes(bundle)
    fetch = ScriptedFetch((429, b""))
    result = crawl.crawl(["2610.00001v1", "2610.00002v1", "2610.00003v1"], tmp_path, fetch, _pacer(FakeClock()))
    assert [p.status for p in result.papers][1:] == [
        "not attempted: run stopped after HTTP 429",
        "not attempted: run stopped after HTTP 429",
    ]
    assert len(fetch.urls) == 1


def test_crawl_extracts_and_parses_each_paper(tmp_path: Path) -> None:
    bundle = _tar_gz({"main.tex": FIXTURE.read_bytes()})
    fetch = ScriptedFetch((200, bundle))
    result = crawl.crawl([PAPER], tmp_path, fetch, _pacer(FakeClock()))
    outcome = result.papers[0]
    assert outcome.status == "ok"
    assert (outcome.found, outcome.parsed, outcome.failed) == (6, 4, 2)
    assert outcome.failure_reasons == {"LaTeXParsingError": 2}
    record = result.records[0]
    assert set(record) == {
        "id",
        "paper_id",
        "file",
        "line",
        "environment",
        "latex",
        "parsed",
        "sympy",
        "parse_error",
    }
    assert record["id"] == f"{PAPER}:main.tex:6"
    assert record["parsed"] is True and record["parse_error"] is None


def test_bad_identifier_is_rejected_without_a_request(tmp_path: Path) -> None:
    fetch = ScriptedFetch()
    result = crawl.crawl(["../etc/passwd"], tmp_path, fetch, _pacer(FakeClock()))
    assert result.papers[0].status == "failed: not an arXiv identifier"
    assert fetch.urls == []


def test_write_catalog_replaces_the_file_with_one_json_object_per_line(tmp_path: Path) -> None:
    path = tmp_path / "catalog" / "equations.jsonl"
    path.parent.mkdir()
    path.write_text("stale\n", encoding="utf-8")
    records = [{"id": "a", "parsed": True}, {"id": "b", "parsed": False}]
    assert crawl.write_catalog(path, records) == 2
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == records
    assert not path.with_name(path.name + ".partial").exists()


def test_parse_rate_arithmetic() -> None:
    assert crawl.parse_rate(3, 4) == 0.75
    assert crawl.parse_rate(0, 4) == 0.0
    assert crawl.parse_rate(0, 0) is None


def test_totals_and_aggregate_rate_across_papers() -> None:
    result = crawl.CrawlResult(
        papers=[
            crawl.PaperOutcome("p1", "ok", found=4, parsed=3, failure_reasons={"LaTeXParsingError": 1}),
            crawl.PaperOutcome("p2", "ok", found=2, parsed=1, failure_reasons={"LaTeXParsingError": 1}),
            crawl.PaperOutcome("p3", "failed: HTTP 404"),
        ],
        records=[],
    )
    totals = result.totals()
    assert totals["papers_listed"] == 3
    assert totals["papers_ok"] == 2
    assert (totals["equations_found"], totals["equations_parsed"], totals["equations_failed"]) == (6, 4, 2)
    assert totals["parse_rate"] == pytest.approx(4 / 6)
    assert totals["failure_reasons"] == {"LaTeXParsingError": 2}


def test_report_has_per_paper_counts_and_the_paper_list(tmp_path: Path) -> None:
    result = crawl.CrawlResult(papers=[crawl.PaperOutcome("p1", "ok", found=2, parsed=2)], records=[])
    payload = crawl.write_report(tmp_path / "report.json", result, paper_list="ids.txt")
    assert payload["paper_list"] == "ids.txt"
    assert payload["papers"][0]["failed"] == 0
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8")) == payload
