"""Experiment: can export formulas be parsed by sympy, and do parsed forms recur across papers?"""

import collections
import json
import re
import signal
from collections.abc import Iterable

import sympy as sp
from sympy.core.relational import Relational
from sympy.logic.boolalg import BooleanAtom
from sympy.parsing.latex import parse_latex

EXPORT = "/home/mark/projects/tool-lit-review/papers/knowledge/collected.json"


def clean(s: str) -> str:
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\(begin|end)\{(equation|align|aligned|gather|split)\*?\}", "", s)
    s = re.sub(r"\\\[|\\\]", "", s)
    s = s.replace("&", "")
    s = re.sub(r"\\\\", " ", s)
    return s.strip().strip("$").strip()


def load_formula_items() -> list[dict]:
    """Return the export's formula items. Reads EXPORT; no import-time side effects."""
    with open(EXPORT, encoding="utf-8") as handle:
        return [i for i in json.load(handle)["items"] if i.get("kind") == "formula"]


def identity_key(expr: sp.Basic) -> str | None:
    """Structural key for a parsed formula, or None when the parse has no structure to key on.

    A chained relation such as `a = b = c` comes back from parse_latex as sympy `false`: Python's chained comparison
    calls bool() on the first Equality, which is False for any non-identical sides. Every such formula would then share
    the key of `false`, so a boolean result gets no key. Relations are keyed without simplify, which hangs on them.
    """
    if isinstance(expr, BooleanAtom):
        return None
    if isinstance(expr, Relational):
        return sp.srepr(expr)
    try:
        return sp.srepr(sp.simplify(expr))
    except Exception:
        return sp.srepr(expr)


def shared_identity_groups(entries: Iterable[tuple[str, str, sp.Basic]]) -> list[set[str]]:
    """Group (paper_id, item_id, expr) entries by identity key; return the papers of each key seen in 2+ papers.

    Entries with no key (None) are never grouped.
    """
    groups: dict[str, set[str]] = collections.defaultdict(set)
    for paper, _item_id, expr in entries:
        key = identity_key(expr)
        if key is not None:
            groups[key].add(paper)
    return [papers for papers in groups.values() if len(papers) > 1]


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def main() -> None:
    signal.signal(signal.SIGALRM, _alarm)
    items = load_formula_items()
    parsed, failures = [], collections.Counter()
    for item in items:
        text = clean(item["latex"])
        if not text:
            failures["empty after cleaning"] += 1
            continue
        signal.alarm(5)
        try:
            expr = parse_latex(text)
            signal.alarm(0)
            parsed.append((item["source"]["paper_id"], item["id"], expr))
        except Timeout:
            failures["timeout"] += 1
        except Exception as error:  # parser refusal is the measurement
            signal.alarm(0)
            failures[type(error).__name__] += 1

    print(f"formula items: {len(items)}; parsed: {len(parsed)}; failed: {len(items) - len(parsed)}")
    print("failure kinds:", dict(failures))

    keyed = [(paper, item_id, expr) for paper, item_id, expr in parsed if identity_key(expr) is not None]
    shared = shared_identity_groups(keyed)
    print(f"parsed with a structural key: {len(keyed)}; forms seen in 2+ papers: {len(shared)}")
    for papers in shared:
        print("  shared across", sorted(papers))


if __name__ == "__main__":
    main()
