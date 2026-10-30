"""Display equations in a paper's TeX source, and whether sympy can parse each one.

Design Intent:
- The matching rules mirror tool-lit-review's candidate extractor (tool_lit_review/tex_formulas.py): the same display
  environments, the same skips (commented lines, the preamble, macro definitions, revision markup), and the same
  whitespace dedupe. That repo owns the rules and this module must not import it, so the copy is kept small on purpose.
  A rule change there is a change here.
- The LaTeX is copied exactly from the source. Parsing is a separate step, so a parse failure never drops an equation
  from the catalog: it is recorded with its failure category.
- "Parsed" means sympy's parse_latex returned a usable expression. A boolean result (a chained relation such as
  a = b = c comes back as sympy `false`) is a failure, because it has no structure to compare.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from sympy.logic.boolalg import BooleanAtom
from sympy.parsing.latex import parse_latex

DISPLAY_ENVIRONMENTS = (
    "equation",
    "align",
    "gather",
    "multline",
    "eqnarray",
    "displaymath",
)
_ENV_PATTERN = re.compile(
    r"\\begin\{(" + "|".join(DISPLAY_ENVIRONMENTS) + r")(\*?)\}.*?\\end\{\1\2\}",
    re.DOTALL,
)
_BRACKET_PATTERN = re.compile(r"\\\[.*?\\\]", re.DOTALL)
_DOLLAR_PATTERN = re.compile(r"\$\$.*?\$\$", re.DOTALL)
# Publisher and editorial markup: an equation inside one of these is a revision marker, not canonical content.
MARKUP_ENVIRONMENTS = ("revision", "changes", "comment")
# Preamble and macro-definition commands: a match that contains one is never an equation.
PREAMBLE_COMMANDS = re.compile(
    r"\\(?:documentclass|usepackage|renewcommand|newcommand|providecommand|DeclareMathOperator|"
    r"newenvironment|renewenvironment|def|let)\b"
)
_LABEL = re.compile(r"\\label\{[^}]*\}")
_WRAPPERS = re.compile(r"\\(?:begin|end)\{(?:equation|align|aligned|gather|split)\*?\}")
_DELIMITERS = re.compile(r"\\\[|\\\]|\$\$")


@dataclass(frozen=True)
class DisplayEquation:
    """One display equation as written in a TeX file, with its location."""

    file: str
    line: int
    environment: str
    latex: str


@dataclass(frozen=True)
class ParseResult:
    """Outcome of parsing one equation. ``error`` is a failure category, set only when ``ok`` is False."""

    ok: bool
    sympy: str | None
    error: str | None


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _is_commented(text: str, index: int) -> bool:
    line_start = text.rfind("\n", 0, index) + 1
    return text[line_start:index].lstrip().startswith("%")


def _markup_spans(text: str) -> list[tuple[int, int]]:
    """The character spans of every markup environment, from its \\begin to its \\end."""
    spans = []
    for name in MARKUP_ENVIRONMENTS:
        for begin in re.finditer(rf"\\begin\{{{name}\}}", text):
            end = re.search(rf"\\end\{{{name}\}}", text[begin.end() :])
            if end:
                spans.append((begin.start(), begin.end() + end.end()))
    return spans


def display_equations(text: str, file: str) -> list[DisplayEquation]:
    """Every display equation in one TeX file, in order of appearance.

    Skipped: commented-out matches; anything before \\begin{document}; any match that contains a preamble or
    macro-definition command; and any match inside a markup environment such as revision.
    """
    found: list[tuple[int, int, str, str]] = []
    for match in _ENV_PATTERN.finditer(text):
        found.append((match.start(), match.end(), match.group(1) + match.group(2), match.group(0)))
    for pattern, label in ((_BRACKET_PATTERN, "bracket"), (_DOLLAR_PATTERN, "dollar")):
        for match in pattern.finditer(text):
            found.append((match.start(), match.end(), label, match.group(0)))
    found.sort()
    body_start = text.find("\\begin{document}")
    markup = _markup_spans(text)
    equations = []
    for start, _end, environment, latex in found:
        if _is_commented(text, start):
            continue
        if body_start >= 0 and start < body_start:
            continue
        if PREAMBLE_COMMANDS.search(latex):
            continue
        if any(begin <= start < stop for begin, stop in markup):
            continue
        equations.append(DisplayEquation(file=file, line=_line_of(text, start), environment=environment, latex=latex))
    return equations


def display_equations_for_paper(sources: Mapping[str, str]) -> list[DisplayEquation]:
    """Display equations across a paper's TeX files, in file-name order.

    An equation whose LaTeX (whitespace collapsed) already appeared earlier in the paper is kept once, at first sight.
    """
    seen: set[str] = set()
    result: list[DisplayEquation] = []
    for name in sorted(sources):
        for equation in display_equations(sources[name], name):
            key = re.sub(r"\s+", " ", equation.latex).strip()
            if key in seen:
                continue
            seen.add(key)
            result.append(equation)
    return result


def clean_latex(latex: str) -> str:
    """The body of one equation, in the form parse_latex accepts: labels, wrappers and delimiters removed.

    Alignment ampersands are dropped and line breaks become spaces. Matches the cleaning used by the parse experiment
    (docs/experiments/parse_latex_identity.py).
    """
    text = _LABEL.sub("", latex)
    text = _WRAPPERS.sub("", text)
    text = _DELIMITERS.sub("", text)
    text = text.replace("&", "")
    text = text.replace("\\\\", " ")
    return text.strip().strip("$").strip()


def parse(latex: str) -> ParseResult:
    """Parse one equation with sympy. Any failure is returned as a category, never raised."""
    cleaned = clean_latex(latex)
    if not cleaned:
        return ParseResult(ok=False, sympy=None, error="empty after cleaning")
    try:
        expression = parse_latex(cleaned)
    except Exception as error:  # sympy raises several exception types for unparseable LaTeX
        return ParseResult(ok=False, sympy=None, error=type(error).__name__)
    if isinstance(expression, BooleanAtom):
        return ParseResult(ok=False, sympy=None, error="boolean result (chained relation)")
    return ParseResult(ok=True, sympy=str(expression), error=None)
