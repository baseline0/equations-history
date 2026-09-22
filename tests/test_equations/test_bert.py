"""Tests for BERT equations."""

import pytest
from equations_history.equations.bert import BERTEquations, get_all_equations


def test_scaled_dot_product_attention() -> None:
    """Test scaled dot-product attention equation."""
    eq = BERTEquations.scaled_dot_product_attention()
    assert eq.name == "Scaled Dot-Product Attention"
    assert "softmax" in eq.latex
    assert "QK" in eq.latex or "K^\\top" in eq.latex
    assert "attention" in eq.concepts
    assert eq.source_line == 30


def test_multi_head_attention() -> None:
    """Test multi-head attention equation."""
    eq = BERTEquations.multi_head_attention()
    assert "Multi" in eq.name and "Head" in eq.name
    assert "Concat" in eq.latex or "concat" in eq.latex
    assert "multi-head" in eq.concepts
    assert eq.source_line == 55


def test_positional_encoding() -> None:
    """Test positional encoding equation."""
    eq = BERTEquations.positional_encoding()
    assert "Positional" in eq.name
    assert "sin" in eq.latex or "sin" in eq.description
    assert "cos" in eq.latex or "cos" in eq.description
    assert "position" in eq.concepts
    assert eq.source_line == 80


def test_masked_language_modeling_loss() -> None:
    """Test masked language modeling loss equation."""
    eq = BERTEquations.masked_language_modeling_loss()
    assert "MLM" in eq.name
    assert "masked" in eq.latex or "masked" in eq.description
    assert "masked language modeling" in eq.concepts
    assert eq.source_line == 105


def test_next_sentence_prediction_loss() -> None:
    """Test next sentence prediction loss equation."""
    eq = BERTEquations.next_sentence_prediction_loss()
    assert "NSP" in eq.name
    assert "IsNext" in eq.latex or "NotNext" in eq.latex
    assert "NSP" in eq.concepts
    assert eq.source_line == 130


def test_bert_total_pretraining_loss() -> None:
    """Test BERT total pretraining loss equation."""
    eq = BERTEquations.bert_total_pretraining_loss()
    assert "Total" in eq.name or "pretraining" in eq.name.lower()
    assert "MLM" in eq.latex
    assert "NSP" in eq.latex
    assert "pretraining" in eq.concepts
    assert eq.source_line == 155


def test_bert_fine_tuning() -> None:
    """Test BERT fine-tuning equation."""
    eq = BERTEquations.bert_fine_tuning()
    assert "Fine" in eq.name or "fine-tuning" in eq.name.lower()
    assert "CLS" in eq.latex or "[CLS]" in eq.latex
    assert "fine-tuning" in eq.concepts or "transfer learning" in eq.concepts
    assert eq.source_line == 175


def test_get_all_equations() -> None:
    """Test that all BERT equations are exported."""
    equations = get_all_equations()
    assert len(equations) >= 7  # At least 7 equations
    assert "scaled_dot_product_attention" in equations
    assert "multi_head_attention" in equations
    assert "positional_encoding" in equations
    assert "masked_language_modeling_loss" in equations
    assert "next_sentence_prediction_loss" in equations
    assert "bert_total_pretraining_loss" in equations
    assert "bert_fine_tuning" in equations


def test_equation_metadata_completeness() -> None:
    """Test that all BERT equations have complete metadata."""
    equations = get_all_equations()
    for name, eq in equations.items():
        assert eq.name, f"{name} missing name"
        assert eq.latex, f"{name} missing latex"
        assert eq.description, f"{name} missing description"
        assert eq.history, f"{name} missing history"
        assert eq.citations, f"{name} missing citations"
        assert eq.source_line > 0, f"{name} missing source_line"
        assert eq.concepts, f"{name} missing concepts"
