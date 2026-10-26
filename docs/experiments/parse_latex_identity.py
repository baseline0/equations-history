"""Experiment: can export formulas be parsed by sympy, and do parsed forms recur across papers?"""

import collections
import json
import re
import signal

import sympy as sp
from sympy.parsing.latex import parse_latex

EXPORT = "/home/mark/projects/tool-lit-review/papers/knowledge/collected.json"


def clean(s: str) -> str:
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\(begin|end)\{(equation|align|aligned|gather|split)\*?\}", "", s)
    s = re.sub(r"\\\[|\\\]", "", s)
    s = s.replace("&", "")
    s = re.sub(r"\\\\", " ", s)
    return s.strip().strip("$").strip()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)

with open(EXPORT, encoding="utf-8") as handle:
    items = [i for i in json.load(handle)["items"] if i.get("kind") == "formula"]
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

# Canonical key: simplified sympy expression, printed with a fixed order. Equal keys are treated as the same equation.
groups = collections.defaultdict(set)
for paper, item_id, expr in parsed:
    try:
        key = sp.srepr(sp.simplify(expr))
    except Exception:
        key = sp.srepr(expr)
    groups[key].add(paper)
shared = [p for p in groups.values() if len(p) > 1]
print(f"distinct canonical forms: {len(groups)}; forms seen in 2+ papers: {len(shared)}")
