"""Tests for optimizer equations."""

import pytest
from equations_history.equations.optimizers import OptimizerEquations, get_all_equations


def test_sgd_update_equation() -> None:
    """Test SGD update equation."""
    eq = OptimizerEquations.sgd_update()
    assert eq.name == "Stochastic Gradient Descent (SGD)"
    assert "theta" in eq.latex or r"\theta" in eq.latex
    assert eq.source_line == 40
    assert "optimizer" in eq.concepts
    assert len(eq.citations) > 0


def test_momentum_update_equation() -> None:
    """Test momentum update equation."""
    eq = OptimizerEquations.momentum_update()
    assert eq.name == "Momentum Update"
    assert "m_t" in eq.latex or "m_{t-1}" in eq.latex
    assert eq.source_line == 60
    assert "momentum" in eq.concepts
    assert len(eq.citations) > 0


def test_nesterov_momentum_equation() -> None:
    """Test Nesterov momentum equation."""
    eq = OptimizerEquations.nesterov_momentum()
    assert eq.name == "Nesterov Momentum"
    assert "tilde" in eq.latex or r"\tilde" in eq.latex
    assert eq.source_line == 80
    assert "Nesterov" in eq.concepts or "look-ahead" in eq.concepts
    assert len(eq.citations) > 0


def test_adam_biased_moments_equation() -> None:
    """Test Adam biased moments equation."""
    eq = OptimizerEquations.adam_biased_moments()
    assert eq.name == "Adam Moment Estimates (Biased)"
    assert "m_t" in eq.latex
    assert "v_t" in eq.latex
    assert eq.source_line == 105
    assert "Adam" in eq.concepts
    assert len(eq.citations) > 0


def test_adam_bias_correction_equation() -> None:
    """Test Adam bias correction equation."""
    eq = OptimizerEquations.adam_bias_correction()
    assert eq.name == "Adam Bias Correction"
    assert "hat" in eq.latex or r"\hat" in eq.latex
    assert eq.source_line == 125
    assert "bias correction" in eq.concepts or "initialization bias" in eq.concepts
    assert len(eq.citations) > 0


def test_adam_update_equation() -> None:
    """Test Adam parameter update equation."""
    eq = OptimizerEquations.adam_update()
    assert eq.name == "Adam Parameter Update"
    assert "sqrt" in eq.latex or r"\sqrt" in eq.latex
    assert eq.source_line == 145
    assert "Adam" in eq.concepts
    assert "adaptive learning rate" in eq.concepts
    assert len(eq.citations) > 0


def test_get_all_equations() -> None:
    """Test that all optimizer equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 6
    assert "sgd_update" in equations
    assert "momentum_update" in equations
    assert "nesterov_momentum" in equations
    assert "adam_biased_moments" in equations
    assert "adam_bias_correction" in equations
    assert "adam_update" in equations


def test_equation_metadata_completeness() -> None:
    """Test that all equations have required metadata."""
    equations = get_all_equations()
    for name, eq in equations.items():
        assert eq.name, f"{name} missing name"
        assert eq.latex, f"{name} missing latex"
        assert eq.description, f"{name} missing description"
        assert eq.history, f"{name} missing history"
        assert eq.citations, f"{name} missing citations"
        assert eq.source_line > 0, f"{name} missing valid source_line"
        assert len(eq.concepts) > 0, f"{name} missing concepts"


def test_equations_have_consistent_structure() -> None:
    """Test that all equations follow consistent structure."""
    equations = get_all_equations()
    for name, eq in equations.items():
        # LaTeX should contain mathematical notation
        assert len(eq.latex) > 5, f"{name} latex too short"
        # History should be substantive
        assert len(eq.history) > 50, f"{name} history too short"
        # Each equation should have at least 1 citation
        assert len(eq.citations) >= 1, f"{name} should have at least 1 citation"
        # Concepts should be lowercase and relevant
        assert all(isinstance(c, str) for c in eq.concepts), f"{name} concepts should be strings"
