"""Tests for diffusion model equations."""

import pytest
from equations_history.equations.diffusion import DiffusionEquations, get_all_equations


def test_forward_process_markov_equation() -> None:
    """Test forward process Markov chain equation."""
    eq = DiffusionEquations.forward_process_markov()
    assert eq.name == "Diffusion Forward Process (Markov)"
    assert "beta" in eq.latex or r"\beta" in eq.latex
    assert "mathcal{N}" in eq.latex
    assert eq.source_line == 40
    assert "diffusion" in eq.concepts
    assert "forward process" in eq.concepts
    assert len(eq.citations) > 0


def test_forward_process_closed_form_equation() -> None:
    """Test forward process closed form equation."""
    eq = DiffusionEquations.forward_process_closed_form()
    assert eq.name == "Forward Process (Closed Form)"
    assert "alpha" in eq.latex or r"\alpha" in eq.latex
    assert "bar" in eq.latex or r"\bar" in eq.latex
    assert "epsilon" in eq.latex
    assert eq.source_line == 60
    assert "forward process" in eq.concepts
    assert len(eq.citations) > 0


def test_reverse_process_equation() -> None:
    """Test reverse process equation."""
    eq = DiffusionEquations.reverse_process()
    assert eq.name == "Diffusion Reverse Process"
    assert "p_" in eq.latex or "p_{" in eq.latex
    assert "mu" in eq.latex or r"\mu" in eq.latex
    assert "Sigma" in eq.latex or r"\Sigma" in eq.latex
    assert eq.source_line == 80
    assert "reverse process" in eq.concepts or "diffusion" in eq.concepts
    assert len(eq.citations) > 0


def test_noise_prediction_objective_equation() -> None:
    """Test noise prediction objective equation."""
    eq = DiffusionEquations.noise_prediction_objective()
    assert eq.name == "Noise Prediction Objective"
    assert "epsilon" in eq.latex
    assert "mathcal{L}" in eq.latex or "L" in eq.latex
    assert eq.source_line == 100
    assert "diffusion" in eq.concepts or "noise prediction" in eq.concepts
    assert len(eq.citations) > 0


def test_score_matching_equation() -> None:
    """Test score matching objective equation."""
    eq = DiffusionEquations.score_matching()
    assert eq.name == "Score Matching Objective"
    assert "score" in eq.name.lower()
    assert "s_" in eq.latex or "s_{" in eq.latex
    assert "mathcal{L}" in eq.latex  # Loss function
    assert eq.source_line == 120
    assert "score matching" in eq.concepts or "score function" in eq.concepts
    assert len(eq.citations) > 0


def test_variance_schedule_equation() -> None:
    """Test variance schedule equation."""
    eq = DiffusionEquations.variance_schedule()
    assert eq.name == "Variance Schedule"
    assert "beta" in eq.latex or r"\beta" in eq.latex
    assert eq.source_line == 140
    assert "variance schedule" in eq.concepts or "noise schedule" in eq.concepts
    assert len(eq.citations) > 0


def test_classifier_free_guidance_equation() -> None:
    """Test classifier-free guidance equation."""
    eq = DiffusionEquations.classifier_free_guidance()
    assert eq.name == "Classifier-Free Guidance"
    assert "epsilon" in eq.latex
    assert "hat" in eq.latex or r"\hat" in eq.latex
    assert eq.source_line == 160
    # Check that at least one concept contains "guidance" or "classifier"
    concept_str = " ".join(eq.concepts).lower()
    assert "guidance" in concept_str or "classifier" in concept_str
    assert len(eq.citations) > 0


def test_get_all_equations() -> None:
    """Test that all diffusion equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 7
    assert "forward_process_markov" in equations
    assert "forward_process_closed_form" in equations
    assert "reverse_process" in equations
    assert "noise_prediction_objective" in equations
    assert "score_matching" in equations
    assert "variance_schedule" in equations
    assert "classifier_free_guidance" in equations


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


def test_forward_and_reverse_duality() -> None:
    """Test that forward and reverse processes are complementary."""
    equations = get_all_equations()
    forward_markov = equations["forward_process_markov"]
    forward_closed = equations["forward_process_closed_form"]
    reverse = equations["reverse_process"]

    # Forward processes should use beta
    assert "beta" in forward_markov.latex or r"\beta" in forward_markov.latex
    assert "alpha" in forward_closed.latex or r"\alpha" in forward_closed.latex

    # Reverse process should mirror forward structure
    assert "reverse" in reverse.name.lower()
    assert "process" in reverse.name.lower()


def test_diffusion_training_pipeline() -> None:
    """Test that noise prediction and score matching are alternative objectives."""
    equations = get_all_equations()
    noise_pred = equations["noise_prediction_objective"]
    score_match = equations["score_matching"]

    # Both should be training objectives for diffusion
    assert "prediction" in noise_pred.name.lower() or "objective" in noise_pred.name.lower()
    assert "score" in score_match.name.lower()

    # Should both involve gradients/expectations over data
    assert "mathbb{E}" in noise_pred.latex or "E[" in noise_pred.latex
    assert "mathbb{E}" in score_match.latex or "E[" in score_match.latex


def test_conditioning_mechanism() -> None:
    """Test that classifier-free guidance is well-defined for conditional diffusion."""
    eq = DiffusionEquations.classifier_free_guidance()

    # Should distinguish conditional and unconditional predictions
    assert "c" in eq.latex  # Condition symbol
    assert "emptyset" in eq.latex or r"\emptyset" in eq.latex  # Unconditional marker

    # Should have a scaling parameter
    assert "w" in eq.latex

    # Should show blending mechanism
    assert "-" in eq.latex  # Difference term
