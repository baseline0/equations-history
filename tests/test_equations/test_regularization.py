"""Tests for regularization equations."""

import pytest
from equations_history.equations.regularization import RegularizationEquations, get_all_equations


def test_dropout_training_equation() -> None:
    """Test dropout training equation."""
    eq = RegularizationEquations.dropout_training()
    assert eq.name == "Dropout (Training)"
    assert "Bernoulli" in eq.latex or "m_i" in eq.latex
    assert eq.source_line == 40
    assert "dropout" in eq.concepts
    assert len(eq.citations) > 0


def test_dropout_inference_equation() -> None:
    """Test dropout inference equation."""
    eq = RegularizationEquations.dropout_inference()
    assert eq.name == "Dropout (Inference)"
    assert "test" in eq.latex or "z" in eq.latex
    assert eq.source_line == 60
    assert "dropout" in eq.concepts
    assert "inference" in eq.concepts


def test_l2_regularization_equation() -> None:
    """Test L2 regularization equation."""
    eq = RegularizationEquations.l2_regularization()
    assert eq.name == "L2 Regularization (Weight Decay)"
    assert "lambda" in eq.latex or r"\lambda" in eq.latex
    assert "W" in eq.latex
    assert eq.source_line == 80
    assert "L2 regularization" in eq.concepts or "weight decay" in eq.concepts
    assert len(eq.citations) > 0


def test_batch_normalization_normalize_equation() -> None:
    """Test batch normalization normalization equation."""
    eq = RegularizationEquations.batch_normalization_normalize()
    assert eq.name == "Batch Normalization (Normalization)"
    assert "mu" in eq.latex or r"\mu" in eq.latex
    assert "sigma" in eq.latex or r"\sigma" in eq.latex
    assert eq.source_line == 105
    assert "batch normalization" in eq.concepts
    assert len(eq.citations) > 0


def test_batch_normalization_scale_shift_equation() -> None:
    """Test batch normalization scale and shift equation."""
    eq = RegularizationEquations.batch_normalization_scale_shift()
    assert eq.name == "Batch Normalization (Scale and Shift)"
    assert "gamma" in eq.latex or r"\gamma" in eq.latex
    assert "beta" in eq.latex
    assert eq.source_line == 125
    assert "batch normalization" in eq.concepts
    assert "learnable" in eq.concepts or "scale" in eq.concepts


def test_batch_normalization_inference_equation() -> None:
    """Test batch normalization inference equation."""
    eq = RegularizationEquations.batch_normalization_inference()
    assert eq.name == "Batch Normalization (Inference)"
    assert "running" in eq.latex
    assert eq.source_line == 145
    assert "batch normalization" in eq.concepts
    assert "inference" in eq.concepts or "running statistics" in eq.concepts


def test_get_all_equations() -> None:
    """Test that all regularization equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 6
    assert "dropout_training" in equations
    assert "dropout_inference" in equations
    assert "l2_regularization" in equations
    assert "batch_normalization_normalize" in equations
    assert "batch_normalization_scale_shift" in equations
    assert "batch_normalization_inference" in equations


def test_equation_metadata_completeness() -> None:
    """Test that all equations have required metadata."""
    equations = get_all_equations()
    for name, eq in equations.items():
        assert eq.name, f"{name} missing name"
        assert eq.latex, f"{name} missing latex"
        assert eq.description, f"{name} missing description"
        assert eq.history, f"{name} missing history"
        assert eq.source_line > 0, f"{name} missing valid source_line"
        assert len(eq.concepts) > 0, f"{name} missing concepts"


def test_dropout_progression() -> None:
    """Test that dropout training and inference are complementary."""
    training = RegularizationEquations.dropout_training()
    inference = RegularizationEquations.dropout_inference()

    # Both should mention dropout
    assert "dropout" in training.name.lower() or "dropout" in training.concepts[0].lower()
    assert "dropout" in inference.name.lower() or "dropout" in inference.concepts[0].lower()

    # Training should mention probability/mask, inference should be deterministic
    assert "Bernoulli" in training.latex or "m" in training.latex
    assert inference.description.count("all") > 0  # Use all units


def test_batch_norm_progression() -> None:
    """Test that batch norm equations form a logical sequence."""
    equations = get_all_equations()
    normalize = equations["batch_normalization_normalize"]
    scale_shift = equations["batch_normalization_scale_shift"]
    inference = equations["batch_normalization_inference"]

    # Should progress from normalization to scale/shift to inference
    assert "normali" in normalize.name.lower()  # "normalization" contains "normali"
    assert "scale" in scale_shift.name.lower() or "shift" in scale_shift.name.lower()
    assert "inference" in inference.name.lower()
