"""Tests for the quantum topic built from math-trace's formula catalog.

The residual of each formula is checked in math-trace (tests/unit/test_quantum_formulas.py), and the emitter refuses to
write a formula that fails it. These tests check what this repo does with the snapshot: the manifest pins it, every
formula is registered with its catalog LaTeX and source line, and the narratives carry the citations.
"""

import hashlib
import json

from equations_history import registry
from equations_history.constants import CATALOG_DIR
from equations_history.equations import quantum
from equations_history.formula_catalog import load_catalog

CATALOG = CATALOG_DIR / "quantum.json"
MANIFEST = CATALOG_DIR / "quantum.manifest.json"

EXPECTED_NAMES = [
    "state_normalisation",
    "bloch_vector_x",
    "bloch_vector_y",
    "bloch_vector_z",
    "born_rule_hadamard_plus",
    "hadamard_unitary",
    "pauli_squares",
    "pauli_product",
    "rotation_z_unitary",
    "bell_state_from_hadamard_and_cnot",
    "grover_two_qubits_one_iteration",
    "shor_factor_from_order",
    "qft_unitary_n4",
]


def test_snapshot_matches_its_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())

    assert hashlib.sha256(CATALOG.read_bytes()).hexdigest() == manifest["sha256"]
    assert manifest["source"] == "math-trace catalogs/quantum_formulas.json"


def test_quantum_topic_registers_the_thirteen_catalog_formulas() -> None:
    assert registry.names("quantum") == EXPECTED_NAMES


def test_each_equation_takes_latex_and_source_from_the_catalog() -> None:
    catalog = load_catalog(CATALOG)

    for name, eq in quantum.get_all_equations().items():
        entry = catalog[name]
        assert eq.id == f"quantum.{name}"
        assert eq.latex == entry.latex
        assert eq.description == entry.description
        assert eq.source == (quantum.MATH_TRACE_MODEL, entry.source_line)


def test_every_equation_has_citations_and_concepts() -> None:
    for name, eq in quantum.get_all_equations().items():
        assert eq.name.strip(), name
        assert eq.history.strip(), name
        assert eq.citations, name
        assert eq.concepts, name


def test_grover_and_shor_cite_their_papers() -> None:
    equations = quantum.get_all_equations()

    assert any("Grover" in c and "1996" in c for c in equations["grover_two_qubits_one_iteration"].citations)
    assert any("Shor" in c and "1997" in c for c in equations["shor_factor_from_order"].citations)


def test_display_names_come_from_the_narrative() -> None:
    eq = quantum.get_all_equations()["bloch_vector_x"]

    assert eq.name == "Bloch Vector, x Component"
