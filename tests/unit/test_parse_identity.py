"""Regression: the parse-based identity key must not merge different equations (docs/experiments, TODO Features).

The inputs are literal `latex` values from the knowledge export (tool-lit-review collected.json). Before the fix, the two
chained relations below both parsed to sympy `false` and shared one key, so they were reported as one cross-paper match.
"""

import importlib.util
from types import ModuleType

import pytest
from sympy.parsing.latex import parse_latex

from equations_history.constants import REPO_ROOT

EXPERIMENT = REPO_ROOT / "docs" / "experiments" / "parse_latex_identity.py"

# Export item app_gamma_g, paper 2610.27834v1
GAMMA_G = "\\begin{equation}\n\t\\gamma_g\n\t=\n\t-\\frac{1}{2}\n\t\\oint(1-\\cos\\chi)\\,d\\xi\n\t=\n\t\\frac{\\beta(\\tau_2-\\tau_1)}{2}\n\t(1-\\cos\\chi).\n\t\\label{eq:app_gamma_g}\n\\end{equation}"
# Export item w(l_i, l_{i+1}), paper 2610.28611v1
W_CHAIN = "\\[\n    w(l_i, l_{i+1}) = \\Delta t = t(l_{i+1}) - t(l_i)\n  \\]"


@pytest.fixture(scope="module")
def identity() -> ModuleType:
    """Load the experiment script by path: it is not a package, and it has no import-time side effects."""
    spec = importlib.util.spec_from_file_location("parse_latex_identity", EXPERIMENT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_colliding_export_equations_are_not_a_cross_paper_match(identity: ModuleType) -> None:
    """The false positive: two different equations from two papers must not share a key."""
    entries = [
        ("2610.27834v1", "gamma_g", parse_latex(identity.clean(GAMMA_G))),
        ("2610.28611v1", "w_chain", parse_latex(identity.clean(W_CHAIN))),
    ]
    assert identity.shared_identity_groups(entries) == []


def test_chained_relations_get_no_structural_key(identity: ModuleType) -> None:
    """parse_latex returns sympy `false` for a chained `a = b = c`, which has no structure to key on."""
    assert identity.identity_key(parse_latex(identity.clean(GAMMA_G))) is None
    assert identity.identity_key(parse_latex(identity.clean(W_CHAIN))) is None


def test_identical_relations_across_papers_still_match(identity: ModuleType) -> None:
    """Positive control: the same single relation in two papers is one identity."""
    entries = [
        ("paper_a", "1", parse_latex("E = m c^2")),
        ("paper_b", "2", parse_latex("E = m c^2")),
    ]
    assert identity.shared_identity_groups(entries) == [{"paper_a", "paper_b"}]
