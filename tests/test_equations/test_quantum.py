"""Tests for quantum computing equations.

The metadata classes hold LaTeX and narrative only. These tests check each formula with a sympy residual that must
simplify to zero, mirroring the W6 checks in math-trace (src/math_trace/quantum_formulas.py).
"""

import math
from collections.abc import Callable

import pytest
import sympy as sp

from equations_history.core import Equation
from equations_history.equations.quantum import QuantumEquations, get_all_equations
from test_equations.source_check import assert_source_is_equation_call

theta, phi = sp.symbols("theta phi", real=True)
I = sp.I  # noqa: E741 - the imaginary unit, named as in the physics


def _is_zero(expr: sp.Expr | sp.MatrixBase) -> bool:
    """A matrix is zero when every entry is; a scalar is zero when it simplifies to 0."""
    if isinstance(expr, sp.MatrixBase):
        return all(_is_zero(entry) for entry in expr)
    return sp.simplify(sp.expand_complex(sp.expand_trig(expr))) == 0


def _bloch_state() -> sp.Matrix:
    return sp.Matrix([sp.cos(theta / 2), sp.exp(I * phi) * sp.sin(theta / 2)])


def _expectation(operator: sp.Matrix) -> sp.Expr:
    return (_bloch_state().H * operator * _bloch_state())[0]


X = sp.Matrix([[0, 1], [1, 0]])
Y = sp.Matrix([[0, -I], [I, 0]])
Z = sp.Matrix([[1, 0], [0, -1]])
ID2 = sp.eye(2)
HADAMARD = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
CNOT = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])


def _rotation_z(angle: sp.Expr) -> sp.Matrix:
    return sp.diag(sp.exp(-I * angle / 2), sp.exp(I * angle / 2))


def _qft(n: int) -> sp.Matrix:
    omega = sp.exp(2 * sp.pi * I / n)
    return sp.Matrix(n, n, lambda j, k: omega ** (j * k)) / sp.sqrt(n)


def test_state_normalisation_residual_is_zero() -> None:
    """cos^2(theta/2) + sin^2(theta/2) = 1."""
    residual = sp.cos(theta / 2) ** 2 + sp.sin(theta / 2) ** 2 - 1
    assert _is_zero(residual)


def test_bloch_vector_components_match_the_state() -> None:
    """The expectations of X, Y, Z in the Bloch state give the sphere coordinates."""
    assert _is_zero(_expectation(X) - sp.sin(theta) * sp.cos(phi))
    assert _is_zero(_expectation(Y) - sp.sin(theta) * sp.sin(phi))
    assert _is_zero(_expectation(Z) - sp.cos(theta))


def test_born_rule_gives_half_for_hadamard_on_zero() -> None:
    """The Hadamard gate on |0> gives outcome 0 with probability one half."""
    amplitude = (HADAMARD * sp.Matrix([1, 0]))[0]
    assert _is_zero(sp.Abs(amplitude) ** 2 - sp.Rational(1, 2))


def test_hadamard_is_unitary() -> None:
    """H^dagger H = I."""
    assert _is_zero(HADAMARD.H * HADAMARD - ID2)


def test_pauli_matrices_square_to_identity() -> None:
    """X^2 = Y^2 = Z^2 = I."""
    for pauli in (X, Y, Z):
        assert _is_zero(pauli * pauli - ID2)


def test_pauli_product_is_i_times_z() -> None:
    """XY = iZ."""
    assert _is_zero(X * Y - I * Z)


def test_z_rotation_is_unitary() -> None:
    """R_z(theta)^dagger R_z(theta) = I."""
    assert _is_zero(_rotation_z(theta).H * _rotation_z(theta) - ID2)


def test_bell_state_from_hadamard_and_cnot() -> None:
    """CNOT (H tensor I) |00> = (|00> + |11>)/sqrt(2)."""
    state = CNOT * sp.kronecker_product(HADAMARD, ID2) * sp.Matrix([1, 0, 0, 0])
    assert _is_zero(state - sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2))


def test_grover_one_iteration_finds_the_item_for_four_items() -> None:
    """With sin(theta) = 1/sqrt(4) and k = 1, sin^2(3 theta) = 1."""
    assert _is_zero(sp.sin(3 * sp.asin(sp.Rational(1, 2))) ** 2 - 1)


def test_shor_factors_15_from_order_of_2() -> None:
    """The order of 2 mod 15 is 4, and gcd(3, 15) * gcd(5, 15) = 15."""
    assert math.gcd(2**2 - 1, 15) * math.gcd(2**2 + 1, 15) == 15


def test_quantum_fourier_transform_is_unitary_for_n4() -> None:
    """F_4^dagger F_4 = I."""
    assert _is_zero(_qft(4).H * _qft(4) - sp.eye(4))


@pytest.mark.parametrize(
    ("method", "expected_name"),
    [
        (QuantumEquations.state_normalisation, "Qubit State Normalisation"),
        (QuantumEquations.bloch_vector_x, "Bloch Vector, x Component"),
        (QuantumEquations.bloch_vector_y, "Bloch Vector, y Component"),
        (QuantumEquations.bloch_vector_z, "Bloch Vector, z Component"),
        (QuantumEquations.born_rule_hadamard_plus, "Born Rule (Hadamard on |0>)"),
        (QuantumEquations.hadamard_unitary, "Hadamard Gate Is Unitary"),
        (QuantumEquations.pauli_squares, "Pauli Matrices Square to Identity"),
        (QuantumEquations.pauli_product, "Pauli Product Rule"),
        (QuantumEquations.rotation_z_unitary, "Z-Rotation Gate Is Unitary"),
        (QuantumEquations.bell_state_from_hadamard_and_cnot, "Bell State from Hadamard and CNOT"),
        (QuantumEquations.grover_two_qubits_one_iteration, "Grover Search, Two Qubits, One Iteration"),
        (QuantumEquations.shor_factor_from_order, "Shor Factoring from Order (N = 15)"),
        (QuantumEquations.qft_unitary_n4, "Quantum Fourier Transform Is Unitary (N = 4)"),
    ],
)
def test_equation_has_name_source_and_citation(method: Callable[[], Equation], expected_name: str) -> None:
    """Each formula carries its display name, a citation, a concept list, and a source line."""
    eq = method()
    assert eq.name == expected_name
    assert eq.citations
    assert eq.concepts
    assert_source_is_equation_call(eq)


def test_shor_and_grover_cite_their_papers() -> None:
    """Grover (1996) and Shor (1997) are cited where their results are used."""
    assert any("Grover" in c and "1996" in c for c in QuantumEquations.grover_two_qubits_one_iteration().citations)
    assert any("Shor" in c and "1997" in c for c in QuantumEquations.shor_factor_from_order().citations)


def test_source_points_at_equation_call_for_every_equation() -> None:
    """Each equation's computed source resolves to its own Equation( call."""
    for eq in get_all_equations().values():
        assert_source_is_equation_call(eq)


def test_get_all_equations_returns_thirteen_formulas() -> None:
    """All thirteen formulas from math-trace W6 are registered under stable keys."""
    assert set(get_all_equations()) == {
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
    }
