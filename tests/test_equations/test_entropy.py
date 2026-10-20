"""Tests for entropy and information equations.

The metadata classes hold LaTeX and narrative only, so these tests evaluate the
same formulas numerically on small discrete distributions.
"""

import inspect
import math
import random

import pytest

from equations_history.equations import entropy as entropy_module
from equations_history.equations.entropy import EntropyEquations, get_all_equations


def shannon(p: list[float]) -> float:
    """Shannon entropy in nats."""
    return -sum(x * math.log(x) for x in p if x > 0)


def joint_entropy(joint: list[list[float]]) -> float:
    """Entropy of a joint distribution given as a matrix."""
    return shannon([p for row in joint for p in row])


def marginal_x(joint: list[list[float]]) -> list[float]:
    return [sum(row) for row in joint]


def marginal_y(joint: list[list[float]]) -> list[float]:
    return [sum(row[j] for row in joint) for j in range(len(joint[0]))]


def conditional_entropy(joint: list[list[float]]) -> float:
    """shannon(X|Y) = shannon(X,Y) - shannon(Y)."""
    return joint_entropy(joint) - shannon(marginal_y(joint))


def mutual_information(joint: list[list[float]]) -> float:
    """I(X;Y) = shannon(X) - shannon(X|Y)."""
    return shannon(marginal_x(joint)) - conditional_entropy(joint)


def kl(p: list[float], q: list[float]) -> float:
    """D(P||Q) in nats."""
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q, strict=True) if pi > 0)


JOINT_2X2 = [[0.1, 0.2], [0.3, 0.4]]


def test_entropy_uniform_over_four_outcomes_is_log_four() -> None:
    """H of a uniform distribution over 4 outcomes equals log 4."""
    assert shannon([0.25] * 4) == pytest.approx(math.log(4))


def test_entropy_deterministic_outcome_is_zero() -> None:
    """A point mass has zero entropy."""
    assert shannon([1.0, 0.0, 0.0]) == pytest.approx(0.0)


def test_chain_rule_joint_equals_marginal_plus_conditional() -> None:
    """shannon(X,Y) = shannon(X) + shannon(Y|X) for a 2x2 joint distribution."""
    # shannon(Y|X) = sum_x p(x) shannon(Y | X=x)
    px = marginal_x(JOINT_2X2)
    h_y_given_x = sum(px[i] * shannon([JOINT_2X2[i][j] / px[i] for j in range(2)]) for i in range(2))
    assert joint_entropy(JOINT_2X2) == pytest.approx(shannon(px) + h_y_given_x)


def test_conditional_entropy_matches_joint_minus_marginal() -> None:
    """shannon(X|Y) = shannon(X,Y) - shannon(Y), and conditioning never increases entropy."""
    h_x_given_y = conditional_entropy(JOINT_2X2)
    assert h_x_given_y == pytest.approx(joint_entropy(JOINT_2X2) - shannon(marginal_y(JOINT_2X2)))
    assert h_x_given_y <= shannon(marginal_x(JOINT_2X2)) + 1e-12


def test_mutual_information_is_zero_for_independent_variables() -> None:
    """A product joint p(x)q(y) gives I(X;Y) = 0."""
    px = [0.3, 0.7]
    py = [0.6, 0.4]
    product = [[a * b for b in py] for a in px]
    assert mutual_information(product) == pytest.approx(0.0, abs=1e-12)


def test_mutual_information_is_positive_for_dependent_variables() -> None:
    """A correlated joint gives I(X;Y) > 0."""
    assert mutual_information(JOINT_2X2) > 0


def test_kl_divergence_is_zero_when_distributions_are_equal() -> None:
    """D(P||P) = 0."""
    p = [0.2, 0.3, 0.5]
    assert kl(p, p) == pytest.approx(0.0, abs=1e-12)


def test_kl_divergence_is_positive_when_distributions_differ() -> None:
    """D(P||Q) > 0 when P != Q, and it is asymmetric in general."""
    p = [0.2, 0.3, 0.5]
    q = [1 / 3, 1 / 3, 1 / 3]
    forward = kl(p, q)
    assert forward > 0
    assert kl(q, p) != pytest.approx(forward)


def test_jensens_inequality_holds_for_log_over_random_sample() -> None:
    """For concave log, E[log X] <= log E[X] on a random positive sample."""
    rng = random.Random(0)
    sample = [rng.uniform(0.1, 10.0) for _ in range(500)]
    mean_of_log = sum(math.log(x) for x in sample) / len(sample)
    log_of_mean = math.log(sum(sample) / len(sample))
    assert mean_of_log <= log_of_mean


def test_entropy_equation_metadata() -> None:
    """Entropy equation carries its name, citation, and source line."""
    eq = EntropyEquations.entropy()
    assert eq.name == "Entropy"
    assert r"\log p(x)" in eq.latex
    assert "entropy" in eq.concepts
    assert any("Cover" in c for c in eq.citations)


def test_mutual_information_equation_metadata() -> None:
    """Mutual information equation references shannon(X) - shannon(X|Y)."""
    eq = EntropyEquations.mutual_information()
    assert "H(X \\mid Y)" in eq.latex
    assert "mutual information" in eq.concepts


def test_relative_entropy_cites_kullback_leibler() -> None:
    """Relative entropy cites Kullback & Leibler (1951)."""
    eq = EntropyEquations.relative_entropy()
    assert any("Kullback" in c and "1951" in c for c in eq.citations)


def test_jensens_inequality_cites_jensen_1906() -> None:
    """Jensen's inequality cites Jensen (1906)."""
    eq = EntropyEquations.jensens_inequality()
    assert any("Jensen" in c and "1906" in c for c in eq.citations)


def test_source_lines_match_method_definitions() -> None:
    """Each equation's source_line points at its method's def line in the module."""
    source_lines = inspect.getsource(entropy_module).splitlines()
    for name, eq in get_all_equations().items():
        def_line = next(i for i, line in enumerate(source_lines, 1) if f"def {name}()" in line)
        assert eq.source_line == def_line


def test_get_all_equations_returns_six_topics() -> None:
    """All six Phase 5a equations are registered under stable keys."""
    assert set(get_all_equations()) == {
        "entropy",
        "conditional_entropy",
        "joint_entropy",
        "mutual_information",
        "relative_entropy",
        "jensens_inequality",
    }
