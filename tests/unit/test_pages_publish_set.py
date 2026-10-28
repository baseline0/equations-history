"""The published pages are exactly the folder the build recorded: an index, BUILD.json, and one page per record.

The Pages workflow uploads pages/ as a whole, so anything else in that folder would go live. This test fails on a stray
file or on a record page that BUILD.json does not name."""

import json

from equations_history.constants import REPO_ROOT

PAGES = REPO_ROOT / "pages"


def test_pages_holds_only_the_index_the_build_record_and_the_named_records() -> None:
    build = json.loads((PAGES / "BUILD.json").read_text(encoding="utf-8"))
    expected = {"index.html", "BUILD.json", *build["records"]}
    assert {path.name for path in PAGES.iterdir()} == expected


def test_each_named_record_has_a_page_and_nothing_else() -> None:
    build = json.loads((PAGES / "BUILD.json").read_text(encoding="utf-8"))
    for record in build["records"]:
        assert {path.name for path in (PAGES / record).iterdir()} == {"index.html"}, record
