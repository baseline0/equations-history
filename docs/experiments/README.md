# Experiments

## parse_latex_identity.py

Can sympy parse the export's formula items, and do parsed forms recur across papers? Reads the knowledge export at
`../tool-lit-review/papers/knowledge/collected.json`. Run it with a Python 3.13 environment that has `sympy` and
`antlr4-python3-runtime==4.11.1` (the runtime version sympy's LaTeX parser needs; 4.7.2 fails on 3.13):

    uv venv --python 3.13 exp && VIRTUAL_ENV=$PWD/exp uv pip install sympy antlr4-python3-runtime==4.11.1
    exp/bin/python docs/experiments/parse_latex_identity.py

Result (2026-10-26): 115 of 185 items parse; 70 fail (65 LaTeXParsingError, 5 SympifyError). The canonical key gave one
cross-paper match, and it is a false positive: two different equations collapse to one key. Not usable for identity yet.

## parse_latex_inspect.py

Prints the cross-paper groups and sample parse failures. Run it from this directory so it can import the first script.
