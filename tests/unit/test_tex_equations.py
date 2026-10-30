"""Tests for the display-equation extractor and parser. Offline: the input is the checked-in fixture sample_paper.tex."""

from __future__ import annotations

import pytest
import sympy as sp

from equations_history import tex_equations
from equations_history.constants import REPO_ROOT

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "tex_equations" / "sample_paper.tex"


@pytest.fixture(scope="module")
def fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_extractor_output_shape(fixture_text: str) -> None:
    """Each equation carries its file, 1-based line, environment, and exact LaTeX; commented and revision matches are gone."""
    equations = tex_equations.display_equations_for_paper({"sample_paper.tex": fixture_text})
    assert [(e.file, e.line, e.environment) for e in equations] == [
        ("sample_paper.tex", 6, "equation"),
        ("sample_paper.tex", 11, "align*"),
        ("sample_paper.tex", 15, "bracket"),
        ("sample_paper.tex", 18, "dollar"),
        ("sample_paper.tex", 20, "equation"),
        ("sample_paper.tex", 24, "equation"),
    ]
    first = equations[0]
    assert first.latex == "\\begin{equation}\n  E = m c^2 \\label{eq:einstein}\n\\end{equation}"
    assert all(isinstance(e, tex_equations.DisplayEquation) for e in equations)


def test_commented_and_revision_equations_are_skipped(fixture_text: str) -> None:
    latex = [e.latex for e in tex_equations.display_equations(fixture_text, "sample_paper.tex")]
    assert not any("c^{3}" in text for text in latex)
    assert not any("Z = 0" in text for text in latex)


def test_preamble_is_skipped() -> None:
    text = "\\documentclass{article}\n\\[ x = 1 \\]\n\\begin{document}\n\\[ y = 2 \\]\n\\end{document}\n"
    latex = [e.latex for e in tex_equations.display_equations(text, "main.tex")]
    assert latex == ["\\[ y = 2 \\]"]


def test_macro_definition_inside_a_match_is_skipped() -> None:
    text = "\\begin{document}\n\\[ \\newcommand{\\X}{1} \\]\n\\[ z = 3 \\]\n\\end{document}\n"
    latex = [e.latex for e in tex_equations.display_equations(text, "main.tex")]
    assert latex == ["\\[ z = 3 \\]"]


def test_same_latex_in_two_files_is_kept_once_at_first_sight() -> None:
    sources = {"a.tex": "\\begin{document}\n\\[ E=mc^2 \\]\n", "b.tex": "\\begin{document}\n\\[ E=mc^2  \\]\n"}
    equations = tex_equations.display_equations_for_paper(sources)
    assert [e.file for e in equations] == ["a.tex"]


def test_clean_latex_removes_labels_wrappers_delimiters_and_ampersands() -> None:
    cleaned = tex_equations.clean_latex("\\begin{align*}\n  a &= b \\\\\n  c &= d \\label{eq:x}\n\\end{align*}")
    assert " ".join(cleaned.split()) == "a = b c = d"
    assert "&" not in cleaned and "\\label" not in cleaned and "\\begin" not in cleaned


def test_parse_success_returns_sympy_form(fixture_text: str) -> None:
    result = tex_equations.parse("\\begin{equation}\n  E = m c^2 \\label{eq:einstein}\n\\end{equation}")
    assert result.ok is True
    assert result.error is None
    assert result.sympy == str(sp.Eq(sp.Symbol("E"), sp.Symbol("c") ** 2 * sp.Symbol("m")))


def test_parse_failure_is_a_category_not_an_exception() -> None:
    result = tex_equations.parse("\\begin{equation}\n  \\frac{1\n\\end{equation}")
    assert result.ok is False
    assert result.sympy is None
    assert result.error == "LaTeXParsingError"


def test_empty_equation_is_a_failure() -> None:
    result = tex_equations.parse("\\begin{equation}\n\\end{equation}")
    assert result.ok is False
    assert result.error == "empty after cleaning"


def test_boolean_result_is_a_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """sympy can return `false` for a chained relation; that has no structure, so it is not a parse."""
    monkeypatch.setattr(tex_equations, "parse_latex", lambda _text: sp.false)
    result = tex_equations.parse("a = b = c")
    assert result.ok is False
    assert result.error == "boolean result (chained relation)"


def test_fixture_parse_outcomes(fixture_text: str) -> None:
    """The parse outcome of each fixture equation, as sympy returns it in this environment."""
    outcomes = [
        tex_equations.parse(e.latex).ok for e in tex_equations.display_equations(fixture_text, "sample_paper.tex")
    ]
    assert outcomes == [True, True, False, True, True, False]
