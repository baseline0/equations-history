"""Tests for autoencoder equations."""

import pytest
from equations_history.equations.autoencoders import AutoencoderEquations, get_all_equations


def test_deterministic_encoder_equation() -> None:
    """Test deterministic encoder equation."""
    eq = AutoencoderEquations.deterministic_encoder()
    assert eq.name == "Deterministic Encoder"
    assert "f_phi" in eq.latex or "f_\\phi" in eq.latex
    assert eq.source_line == 40
    assert "encoder" in eq.concepts
    assert len(eq.citations) > 0


def test_deterministic_decoder_equation() -> None:
    """Test deterministic decoder equation."""
    eq = AutoencoderEquations.deterministic_decoder()
    assert eq.name == "Deterministic Decoder"
    assert "g_theta" in eq.latex or "g_\\theta" in eq.latex
    assert eq.source_line == 55
    assert "decoder" in eq.concepts


def test_mse_reconstruction_loss() -> None:
    """Test MSE reconstruction loss equation."""
    eq = AutoencoderEquations.mse_reconstruction_loss()
    assert eq.name == "MSE Reconstruction Loss"
    assert "MSE" in eq.latex or "mse" in eq.latex.lower()
    assert eq.source_line == 70
    assert "loss" in eq.concepts


def test_bce_reconstruction_loss() -> None:
    """Test BCE reconstruction loss equation."""
    eq = AutoencoderEquations.bce_reconstruction_loss()
    assert eq.name == "Binary Cross-Entropy Loss"
    assert "BCE" in eq.latex or "log" in eq.latex
    assert eq.source_line == 85
    assert "cross-entropy" in eq.concepts


def test_vae_elbo() -> None:
    """Test VAE ELBO equation."""
    eq = AutoencoderEquations.vae_elbo()
    assert eq.name == "VAE ELBO (Evidence Lower Bound)"
    assert "ELBO" in eq.latex
    assert "KL" in eq.latex
    assert "VAE" in eq.concepts
    assert eq.source_line == 105


def test_vae_kl_divergence_gaussian() -> None:
    """Test VAE KL divergence for Gaussian equation."""
    eq = AutoencoderEquations.vae_kl_divergence_gaussian()
    assert "KL" in eq.name
    assert "Gaussian" in eq.name
    assert "KL divergence" in eq.concepts
    assert eq.source_line == 125


def test_reparameterization_trick() -> None:
    """Test reparameterization trick equation."""
    eq = AutoencoderEquations.reparameterization_trick()
    assert "Reparameterization" in eq.name
    assert "epsilon" in eq.latex or "ε" in eq.latex
    assert "reparameterization trick" in eq.concepts or "gradient flow" in eq.concepts


def test_get_all_equations() -> None:
    """Test that all equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 7  # At least 7 equations
    assert "deterministic_encoder" in equations
    assert "deterministic_decoder" in equations
    assert "mse_reconstruction_loss" in equations
    assert "bce_reconstruction_loss" in equations
    assert "vae_elbo" in equations
    assert "vae_kl_divergence_gaussian" in equations
    assert "reparameterization_trick" in equations


def test_equation_metadata_completeness() -> None:
    """Test that all equations have complete metadata."""
    equations = get_all_equations()
    for name, eq in equations.items():
        assert eq.name, f"{name} missing name"
        assert eq.latex, f"{name} missing latex"
        assert eq.description, f"{name} missing description"
        assert eq.history, f"{name} missing history"
        assert eq.citations, f"{name} missing citations"
        assert eq.source_line > 0, f"{name} missing source_line"
        assert eq.concepts, f"{name} missing concepts"
