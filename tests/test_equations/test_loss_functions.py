"""Tests for loss function equations."""

import pytest
from equations_history.equations.loss_functions import LossFunctionEquations, get_all_equations


def test_cross_entropy_binary_equation() -> None:
    """Test binary cross-entropy equation."""
    eq = LossFunctionEquations.cross_entropy_binary()
    assert eq.name == "Binary Cross-Entropy Loss"
    assert "log" in eq.latex
    assert "y_i" in eq.latex or "y" in eq.latex
    assert eq.source_line == 40
    assert "cross-entropy" in eq.concepts
    assert len(eq.citations) > 0


def test_cross_entropy_multiclass_equation() -> None:
    """Test categorical cross-entropy equation."""
    eq = LossFunctionEquations.cross_entropy_multiclass()
    assert eq.name == "Categorical Cross-Entropy Loss"
    assert "log" in eq.latex
    assert "sum" in eq.latex
    assert eq.source_line == 60
    # Check that at least one concept contains "categorical" or "cross"
    concept_str = " ".join(eq.concepts).lower()
    assert "categorical" in concept_str or "cross" in concept_str
    assert len(eq.citations) > 0


def test_kl_divergence_equation() -> None:
    """Test KL divergence equation."""
    eq = LossFunctionEquations.kl_divergence()
    assert eq.name == "Kullback-Leibler Divergence"
    assert "KL" in eq.latex
    assert "log" in eq.latex
    assert eq.source_line == 80
    assert "KL divergence" in eq.concepts or "relative entropy" in eq.concepts
    assert len(eq.citations) > 0


def test_jensen_shannon_divergence_equation() -> None:
    """Test Jensen-Shannon divergence equation."""
    eq = LossFunctionEquations.jensen_shannon_divergence()
    assert eq.name == "Jensen-Shannon Divergence"
    assert "JS" in eq.latex
    assert "KL" in eq.latex
    assert eq.source_line == 105
    # Check that at least one concept mentions Jensen-Shannon or symmetric
    concept_str = " ".join(eq.concepts).lower()
    assert "jensen" in concept_str or "symmetric" in concept_str
    assert len(eq.citations) > 0


def test_wasserstein_distance_equation() -> None:
    """Test Wasserstein distance equation."""
    eq = LossFunctionEquations.wasserstein_distance()
    assert eq.name == "Wasserstein Distance (1-Wasserstein)"
    assert "W_1" in eq.latex or "Wasserstein" in eq.description
    assert "inf" in eq.latex
    assert eq.source_line == 130
    assert "Wasserstein" in eq.concepts or "optimal transport" in eq.concepts
    assert len(eq.citations) > 0


def test_earth_mover_distance_discrete_equation() -> None:
    """Test discrete Wasserstein/EMD approximation equation."""
    eq = LossFunctionEquations.earth_mover_distance_discrete()
    assert eq.name == "Earth Mover's Distance (Discrete Approximation)"
    assert "bijection" in eq.latex or "phi" in eq.latex or r"\phi" in eq.latex
    assert eq.source_line == 155
    assert "Wasserstein" in eq.concepts or "optimal assignment" in eq.concepts
    assert len(eq.citations) > 0


def test_get_all_equations() -> None:
    """Test that all loss function equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 6
    assert "cross_entropy_binary" in equations
    assert "cross_entropy_multiclass" in equations
    assert "kl_divergence" in equations
    assert "jensen_shannon_divergence" in equations
    assert "wasserstein_distance" in equations
    assert "earth_mover_distance_discrete" in equations


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


def test_cross_entropy_progression() -> None:
    """Test that cross-entropy equations progress from binary to multiclass."""
    equations = get_all_equations()
    binary = equations["cross_entropy_binary"]
    multiclass = equations["cross_entropy_multiclass"]

    # Both should be about cross-entropy
    binary_concepts_str = " ".join(binary.concepts).lower()
    multiclass_concepts_str = " ".join(multiclass.concepts).lower()
    assert "cross" in binary_concepts_str
    assert "cross" in multiclass_concepts_str

    # Binary should mention binary, multiclass should mention categorical
    assert "binary" in binary.name.lower()
    assert "categorical" in multiclass.name.lower() or "multi" in multiclass.name.lower()


def test_divergence_family() -> None:
    """Test that KL and JS divergences are related."""
    equations = get_all_equations()
    kl = equations["kl_divergence"]
    js = equations["jensen_shannon_divergence"]

    # Both should be about probability distributions
    assert "divergence" in kl.name.lower()
    assert "divergence" in js.name.lower()

    # JS should mention it's symmetric/based on KL
    assert "symmetric" in js.description.lower() or "average" in js.description.lower()


def test_wasserstein_theory() -> None:
    """Test that Wasserstein equations form coherent theory."""
    equations = get_all_equations()
    wasserstein = equations["wasserstein_distance"]
    emd = equations["earth_mover_distance_discrete"]

    # Should both be about optimal transport
    assert "Wasserstein" in wasserstein.name or "optimal transport" in wasserstein.concepts
    assert "Wasserstein" in emd.concepts or "Earth Mover" in emd.name

    # EMD should be approximation of continuous Wasserstein
    assert "approximation" in emd.description.lower() or "discrete" in emd.name.lower()
