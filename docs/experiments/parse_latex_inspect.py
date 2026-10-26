import collections

import sympy as sp
from parse_latex_identity import clean, items
from sympy.parsing.latex import parse_latex

by_form = collections.defaultdict(list)
for item in items:
    text = clean(item["latex"])
    try:
        expr = parse_latex(text)
    except Exception:
        continue
    try:
        key = sp.srepr(sp.simplify(expr))
    except Exception:
        key = sp.srepr(expr)
    by_form[key].append((item["source"]["paper_id"], text))
for members in by_form.values():
    if len({p for p, _ in members}) > 1:
        print("SHARED across", sorted({p for p, _ in members}))
        for p, t in members:
            print("   ", p, "|", t[:110].replace("\n", " "))
print("--- sample failures")
n = 0
for item in items:
    text = clean(item["latex"])
    try:
        parse_latex(text)
    except Exception as error:
        print(type(error).__name__, "|", text[:100].replace("\n", " "))
        n += 1
        if n == 12:
            break
