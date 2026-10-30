"""Crawl arXiv papers: fetch TeX source, extract display equations, parse them, and write the catalog and a report.

Design Intent:
- Every path and paper ID is passed in. Nothing here reads the environment. The HTTP function, the pacer's clock and
  its sleep are injected, so the tests run offline.
- arXiv rate guidance: at most one request per second. A cache hit makes no request.
- One retry, after the pacer wait, on a network error or a 5xx response. HTTP 429 stops the whole run: a rate-limit
  response is never retried.
- Only .tex members of a bundle are read, in memory. Nothing from a bundle is written to disk or executed.
- The catalog is JSON Lines, one equation per line, rewritten whole on each run. The report is JSON with per-paper
  counts, aggregate totals and the parse rate.
"""

from __future__ import annotations

import gzip
import io
import json
import re
import tarfile
import time
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from equations_history import tex_equations

ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
EPRINT_URL = "https://arxiv.org/e-print/{paper_id}"
USER_AGENT = "equations-history-crawler/0.1"
TIMEOUT_SECONDS = 60.0
MIN_INTERVAL_SECONDS = 1.0
RETRIES = 1

# (url, timeout seconds) -> (HTTP status, body). Network failures raise OSError (URLError and timeouts included).
Fetch = Callable[[str, float], tuple[int, bytes]]


class RateLimited(RuntimeError):
    """arXiv answered HTTP 429. The run stops; nothing is retried."""


class FetchFailed(RuntimeError):
    """A bundle could not be fetched. The message is the failure reason recorded for the paper."""


class BundleError(ValueError):
    """A downloaded bundle is neither a TeX tar archive nor TeX text."""


def http_fetch(url: str, timeout: float) -> tuple[int, bytes]:
    """GET ``url``. Redirects are followed. Returns the status and body; a 4xx or 5xx is returned, not raised."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, b""


class Pacer:
    """Spaces calls at least ``interval`` seconds apart. The clock and sleep are injectable for tests."""

    def __init__(
        self,
        interval: float = MIN_INTERVAL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._interval = interval
        self._clock = clock
        self._sleep = sleep
        self._last: float | None = None

    def wait(self) -> None:
        """Block until the interval since the previous call has passed, then mark this call as made."""
        if self._last is not None:
            remaining = self._last + self._interval - self._clock()
            if remaining > 0:
                self._sleep(remaining)
        self._last = self._clock()


def fetch_bundle(paper_id: str, cache_dir: Path, fetch: Fetch, pacer: Pacer) -> bytes:
    """The e-print bundle for one paper, from the cache when present, otherwise fetched and cached.

    Raises RateLimited on HTTP 429 and FetchFailed for any other failure after the single retry.
    """
    cached = cache_dir / f"{paper_id}.bundle"
    if cached.is_file():
        return cached.read_bytes()

    url = EPRINT_URL.format(paper_id=paper_id)
    reason = "no attempt made"
    for _attempt in range(RETRIES + 1):
        pacer.wait()
        try:
            status, body = fetch(url, TIMEOUT_SECONDS)
        except OSError as error:
            reason = f"network error: {error}"
            continue
        if status == 429:
            raise RateLimited(url)
        if status == 200:
            cache_dir.mkdir(parents=True, exist_ok=True)
            partial = cached.with_name(cached.name + ".partial")
            partial.write_bytes(body)
            partial.replace(cached)
            return body
        reason = f"HTTP {status}"
        if status < 500:
            break
    raise FetchFailed(reason)


def tex_sources(bundle: bytes) -> dict[str, str]:
    """The .tex members of an e-print bundle, keyed by member name.

    An e-print is a (gzip'd) tar archive, or a single (gzip'd) TeX file, which is returned as ``main.tex``.
    """
    try:
        with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:*") as archive:
            sources: dict[str, str] = {}
            for member in archive.getmembers():
                if not (member.isfile() and member.name.endswith(".tex")):
                    continue
                handle = archive.extractfile(member)
                if handle is not None:
                    sources[member.name] = handle.read().decode("utf-8", errors="replace")
            return sources
    except tarfile.TarError:
        pass
    try:
        raw = gzip.decompress(bundle)
    except OSError:
        raw = bundle
    text = raw.decode("utf-8", errors="replace")
    if "\\" not in text:
        raise BundleError("bundle is neither a tar archive nor TeX text")
    return {"main.tex": text}


@dataclass
class PaperOutcome:
    """What happened to one paper. ``status`` is "ok", "failed: <reason>" or "not attempted: <reason>"."""

    paper_id: str
    status: str
    found: int = 0
    parsed: int = 0
    failure_reasons: dict[str, int] = field(default_factory=dict)

    @property
    def failed(self) -> int:
        return self.found - self.parsed


@dataclass
class CrawlResult:
    """Every paper's outcome, the catalog records, and the aggregate counts."""

    papers: list[PaperOutcome]
    records: list[dict[str, Any]]

    def totals(self) -> dict[str, Any]:
        found = sum(p.found for p in self.papers)
        parsed = sum(p.parsed for p in self.papers)
        reasons: Counter[str] = Counter()
        for paper in self.papers:
            reasons.update(paper.failure_reasons)
        return {
            "papers_listed": len(self.papers),
            "papers_ok": sum(1 for p in self.papers if p.status == "ok"),
            "equations_found": found,
            "equations_parsed": parsed,
            "equations_failed": found - parsed,
            "parse_rate": parse_rate(parsed, found),
            "failure_reasons": dict(reasons.most_common()),
        }


def parse_rate(parsed: int, found: int) -> float | None:
    """Parsed equations as a fraction of found equations. None when nothing was found, so no rate is invented."""
    if found == 0:
        return None
    return parsed / found


def _records_for(paper_id: str, sources: dict[str, str]) -> tuple[list[dict[str, Any]], PaperOutcome]:
    """Catalog records for one paper's equations, and the paper's outcome with failure counts by category."""
    records: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    parsed = 0
    equations = tex_equations.display_equations_for_paper(sources)
    for equation in equations:
        result = tex_equations.parse(equation.latex)
        if result.ok:
            parsed += 1
        elif result.error is not None:
            reasons[result.error] += 1
        records.append(
            {
                "id": f"{paper_id}:{equation.file}:{equation.line}",
                "paper_id": paper_id,
                "file": equation.file,
                "line": equation.line,
                "environment": equation.environment,
                "latex": equation.latex,
                "parsed": result.ok,
                "sympy": result.sympy,
                "parse_error": result.error,
            }
        )
    outcome = PaperOutcome(
        paper_id=paper_id,
        status="ok",
        found=len(equations),
        parsed=parsed,
        failure_reasons=dict(reasons.most_common()),
    )
    return records, outcome


def crawl(paper_ids: Iterable[str], cache_dir: Path, fetch: Fetch, pacer: Pacer) -> CrawlResult:
    """Fetch, extract and parse each paper in order. A rate-limit response stops the run; later papers are listed as not attempted."""
    papers: list[PaperOutcome] = []
    records: list[dict[str, Any]] = []
    ids = list(paper_ids)
    for index, paper_id in enumerate(ids):
        if not ARXIV_ID.match(paper_id):
            papers.append(PaperOutcome(paper_id, "failed: not an arXiv identifier"))
            continue
        try:
            bundle = fetch_bundle(paper_id, cache_dir, fetch, pacer)
        except RateLimited:
            papers.append(PaperOutcome(paper_id, "not attempted: run stopped after HTTP 429"))
            for later in ids[index + 1 :]:
                papers.append(PaperOutcome(later, "not attempted: run stopped after HTTP 429"))
            break
        except FetchFailed as error:
            papers.append(PaperOutcome(paper_id, f"failed: {error}"))
            continue
        try:
            sources = tex_sources(bundle)
        except BundleError as error:
            papers.append(PaperOutcome(paper_id, f"failed: {error}"))
            continue
        if not sources:
            papers.append(PaperOutcome(paper_id, "failed: bundle has no .tex files"))
            continue
        paper_records, outcome = _records_for(paper_id, sources)
        records.extend(paper_records)
        papers.append(outcome)
    return CrawlResult(papers=papers, records=records)


def write_catalog(path: Path, records: Iterable[dict[str, Any]]) -> int:
    """Write one JSON object per line, replacing the file. Returns the number of records written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    count = 0
    with partial.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    partial.replace(path)
    return count


def report_dict(result: CrawlResult, paper_list: str) -> dict[str, Any]:
    """The JSON report: the paper list it came from, the totals, and each paper's counts and failure reasons."""
    return {
        "paper_list": paper_list,
        "totals": result.totals(),
        "papers": [asdict(paper) | {"failed": paper.failed} for paper in result.papers],
    }


def write_report(path: Path, result: CrawlResult, paper_list: str) -> dict[str, Any]:
    """Write the report JSON, replacing the file, and return what was written."""
    payload = report_dict(result, paper_list)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
