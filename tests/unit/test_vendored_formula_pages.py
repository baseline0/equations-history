"""The vendored formula renderer is the copy named in its manifest, and it depends on nothing outside the standard library.

A hand edit to vendor/tool_publish/formula_pages.py fails here, so drift from the recorded copy is caught in CI rather
than in a published page."""

import ast
import hashlib
import json
import sys

from equations_history.constants import REPO_ROOT

VENDOR = REPO_ROOT / "vendor" / "tool_publish"


def _manifest() -> dict:
    return json.loads((VENDOR / "MANIFEST.json").read_text(encoding="utf-8"))


def test_each_vendored_file_matches_its_recorded_sha256() -> None:
    for name, expected in _manifest()["files"].items():
        actual = hashlib.sha256((VENDOR / name).read_bytes()).hexdigest()
        assert actual == expected, f"{name} was edited by hand; re-copy it from its source"


def test_the_vendored_renderer_imports_only_the_standard_library() -> None:
    tree = ast.parse((VENDOR / "formula_pages.py").read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        for alias in (node.names if isinstance(node, ast.Import) else [])
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0
    }
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)
