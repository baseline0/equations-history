"""Quantum computing equations: qubit states, the Bloch sphere, measurement, single- and two-qubit gates,
Grover's search, Shor's order-finding reduction, and the quantum Fourier transform.

Mirrors the key formulas of math-trace (RM-019 W6). Each entry keeps the source given there. Section pinpoints are
not yet verified against the sources. Each formula's sympy check lives in tests/test_equations/test_quantum.py.
"""

from equations_history.core import Equation
from equations_history.registry import equation, equations_for

NIELSEN_CHUANG = "Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation and Quantum Information (10th anniversary ed.). Cambridge University Press."
GROVER = (
    "Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. "
    "Proceedings of the 28th ACM Symposium on Theory of Computing (STOC), 212-219."
)
SHOR = (
    "Shor, P. W. (1997). Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum "
    "computer. SIAM Journal on Computing, 26(5), 1484-1509."
)


class QuantumEquations:
    """Quantum computing definitions: states, measurement, gates, Grover, Shor, and the QFT."""

    @staticmethod
    @equation("quantum")
    def state_normalisation() -> Equation:
        """Normalisation of a single-qubit state.

        Source: quantum.py
        """
        return Equation(
            id="quantum.state_normalisation",
            name="Qubit State Normalisation",
            latex=r"|\alpha|^2 + |\beta|^2 = 1 \text{ for } \alpha|0\rangle + \beta|1\rangle",
            description=(
                "A qubit state is a unit vector in C^2. The squared magnitudes of its amplitudes are the "
                "probabilities of the two measurement outcomes, so they must sum to one."
            ),
            history=(
                "The amplitude postulates were stated by von Neumann (1932) for quantum mechanics in general. "
                "The qubit, a two-level system carrying one of these states, became the unit of quantum "
                "information in the 1990s."
            ),
            citations=[NIELSEN_CHUANG],
            concepts=["qubit", "quantum state", "amplitude", "normalisation", "superposition"],
        )

    @staticmethod
    @equation("quantum")
    def bloch_vector_x() -> Equation:
        """Bloch-sphere x component of a pure qubit state.

        Source: quantum.py
        """
        return Equation(
            id="quantum.bloch_vector_x",
            name="Bloch Vector, x Component",
            latex=r"\langle\psi|X|\psi\rangle = \sin\theta\cos\phi",
            description=(
                "Expectation of the Pauli X operator in the state with polar angle theta and azimuth phi. "
                "Together with the y and z components it places a pure state on the unit sphere."
            ),
            history=(
                "Bloch (1946) introduced the sphere to describe the magnetisation of spin-1/2 nuclei. "
                "Quantum computing adopted it as the standard picture of a single qubit."
            ),
            citations=[NIELSEN_CHUANG, "Bloch, F. (1946). Nuclear induction. Physical Review, 70(7-8), 460-474."],
            concepts=["Bloch sphere", "qubit", "Pauli operator", "expectation value"],
        )

    @staticmethod
    @equation("quantum")
    def bloch_vector_y() -> Equation:
        """Bloch-sphere y component of a pure qubit state.

        Source: quantum.py
        """
        return Equation(
            id="quantum.bloch_vector_y",
            name="Bloch Vector, y Component",
            latex=r"\langle\psi|Y|\psi\rangle = \sin\theta\sin\phi",
            description=(
                "Expectation of the Pauli Y operator in the same state. Paired with the x and z components, "
                "it gives the state's position on the Bloch sphere."
            ),
            history=(
                "The Bloch sphere picture was introduced for nuclear magnetic resonance by Bloch (1946). "
                "Its use for single qubits followed in the quantum information literature."
            ),
            citations=[NIELSEN_CHUANG, "Bloch, F. (1946). Nuclear induction. Physical Review, 70(7-8), 460-474."],
            concepts=["Bloch sphere", "qubit", "Pauli operator", "expectation value"],
        )

    @staticmethod
    @equation("quantum")
    def bloch_vector_z() -> Equation:
        """Bloch-sphere z component of a pure qubit state.

        Source: quantum.py
        """
        return Equation(
            id="quantum.bloch_vector_z",
            name="Bloch Vector, z Component",
            latex=r"\langle\psi|Z|\psi\rangle = \cos\theta",
            description=(
                "Expectation of the Pauli Z operator. It is +1 for |0> and -1 for |1>, so it measures how "
                "far the state leans toward the poles of the sphere."
            ),
            history=(
                "Bloch (1946) introduced the sphere for nuclear spins. The z axis is the standard computational "
                "basis direction in quantum computing."
            ),
            citations=[NIELSEN_CHUANG, "Bloch, F. (1946). Nuclear induction. Physical Review, 70(7-8), 460-474."],
            concepts=["Bloch sphere", "qubit", "computational basis", "Pauli operator"],
        )

    @staticmethod
    @equation("quantum")
    def born_rule_hadamard_plus() -> Equation:
        """Born rule applied to the Hadamard gate acting on |0>.

        Source: quantum.py
        """
        return Equation(
            id="quantum.born_rule_hadamard_plus",
            name="Born Rule (Hadamard on |0>)",
            latex=r"p(0) = |\langle 0|H|0\rangle|^2 = \tfrac12",
            description=(
                "The probability of outcome 0 after the Hadamard gate is the squared magnitude of the amplitude. "
                "The result one half shows that the Hadamard gate prepares an equal superposition."
            ),
            history=(
                "Born (1926) proposed that squared amplitudes give measurement probabilities. This is the "
                "measurement postulate that quantum algorithms rely on at their output."
            ),
            citations=[
                NIELSEN_CHUANG,
                "Born, M. (1926). Zur Quantenmechanik der Stoßvorgänge. Zeitschrift für Physik, 37, 863-867.",
            ],
            concepts=["Born rule", "measurement", "Hadamard gate", "superposition"],
        )

    @staticmethod
    @equation("quantum")
    def hadamard_unitary() -> Equation:
        """The Hadamard gate is unitary.

        Source: quantum.py
        """
        return Equation(
            id="quantum.hadamard_unitary",
            name="Hadamard Gate Is Unitary",
            latex=r"H^\dagger H = I",
            description=(
                "Quantum gates are unitary, so they preserve the norm of a state and can be inverted. The "
                "Hadamard gate satisfies this, and it is its own inverse."
            ),
            history=(
                "The matrix is named after Hadamard, whose matrices of this form appeared in the 1890s. Its role "
                "as a single-qubit gate was standardised in quantum circuit notation during the 1990s."
            ),
            citations=[NIELSEN_CHUANG],
            concepts=["unitary", "Hadamard gate", "single-qubit gate", "reversibility"],
        )

    @staticmethod
    @equation("quantum")
    def pauli_squares() -> Equation:
        """The Pauli matrices square to the identity.

        Source: quantum.py
        """
        return Equation(
            id="quantum.pauli_squares",
            name="Pauli Matrices Square to Identity",
            latex=r"X^2 = Y^2 = Z^2 = I",
            description=(
                "Each Pauli matrix is Hermitian and squares to the identity, so its eigenvalues are plus and minus "
                "one. This is why a Pauli measurement has two outcomes."
            ),
            history=(
                "Pauli (1927) introduced the matrices to describe the spin of the electron. Their algebra "
                "underlies the Pauli gates of quantum computing."
            ),
            citations=[
                NIELSEN_CHUANG,
                "Pauli, W. (1927). Zur Quantenmechanik des magnetischen Elektrons. Zeitschrift für Physik, 43, 601-623.",
            ],
            concepts=["Pauli matrices", "Hermitian operator", "eigenvalue", "spin"],
        )

    @staticmethod
    @equation("quantum")
    def pauli_product() -> Equation:
        """Product of two Pauli matrices gives the third, times i.

        Source: quantum.py
        """
        return Equation(
            id="quantum.pauli_product",
            name="Pauli Product Rule",
            latex=r"XY = iZ",
            description=(
                "The product of two distinct Pauli matrices is i times the third. The sign and factor of i "
                "determine how the gates compose and commute."
            ),
            history=(
                "Pauli (1927) gave the algebra of the spin matrices. The cyclic relation XY = iZ is the "
                "basic identity behind their use as quantum gates."
            ),
            citations=[
                NIELSEN_CHUANG,
                "Pauli, W. (1927). Zur Quantenmechanik des magnetischen Elektrons. Zeitschrift für Physik, 43, 601-623.",
            ],
            concepts=["Pauli matrices", "commutator", "quantum gate", "algebra"],
        )

    @staticmethod
    @equation("quantum")
    def rotation_z_unitary() -> Equation:
        """The z-axis rotation gate is unitary.

        Source: quantum.py
        """
        return Equation(
            id="quantum.rotation_z_unitary",
            name="Z-Rotation Gate Is Unitary",
            latex=r"R_z(\theta)^\dagger R_z(\theta) = I",
            description=(
                "The rotation about the z axis by angle theta is unitary for every theta. It shifts only the phase "
                "of the |1> amplitude, so it moves a state around the equator of the Bloch sphere."
            ),
            history=(
                "The rotation is the exponential of a Pauli matrix, so its unitarity follows from the Pauli "
                "algebra. Parameterised rotations became standard single-qubit gates in quantum circuit design."
            ),
            citations=[NIELSEN_CHUANG],
            concepts=["unitary", "rotation gate", "phase", "Bloch sphere"],
        )

    @staticmethod
    @equation("quantum")
    def bell_state_from_hadamard_and_cnot() -> Equation:
        """A Bell state from a Hadamard and a CNOT.

        Source: quantum.py
        """
        return Equation(
            id="quantum.bell_state_from_hadamard_and_cnot",
            name="Bell State from Hadamard and CNOT",
            latex=r"\mathrm{CNOT}(H\otimes I)|00\rangle = \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)",
            description=(
                "A Hadamard on the first qubit followed by a CNOT produces an entangled Bell state. Neither qubit "
                "has a definite state on its own, but the two measurements always agree."
            ),
            history=(
                "Bell (1964) showed that entangled states give correlations no local hidden-variable theory can "
                "reproduce. The Hadamard-then-CNOT circuit is the standard way to prepare one of these states."
            ),
            citations=[
                NIELSEN_CHUANG,
                "Bell, J. S. (1964). On the Einstein Podolsky Rosen paradox. Physics, 1(3), 195-200.",
            ],
            concepts=["entanglement", "Bell state", "CNOT", "controlled gate", "tensor product"],
        )

    @staticmethod
    @equation("quantum")
    def grover_two_qubits_one_iteration() -> Equation:
        """Grover's search on four items finds the answer in one iteration.

        Source: quantum.py
        """
        return Equation(
            id="quantum.grover_two_qubits_one_iteration",
            name="Grover Search, Two Qubits, One Iteration",
            latex=r"\sin^2\big((2k+1)\theta\big) = 1 \text{ with } \sin\theta = 1/\sqrt{N},\ N=4,\ k=1",
            description=(
                "Grover's iteration rotates the state by 2 theta per step. With N = 4 items, one iteration brings "
                "the amplitude of the marked item to certainty, so the success probability is exactly one."
            ),
            history=(
                "Grover (1996) gave a quadratic speedup for unstructured search. For four items the speedup is "
                "exact after a single iteration, the case used as the textbook example."
            ),
            citations=[GROVER, NIELSEN_CHUANG],
            concepts=["Grover's algorithm", "amplitude amplification", "search", "quantum speedup"],
        )

    @staticmethod
    @equation("quantum")
    def shor_factor_from_order() -> Equation:
        """Factors of 15 recovered from the order of 2 modulo 15.

        Source: quantum.py
        """
        return Equation(
            id="quantum.shor_factor_from_order",
            name="Shor Factoring from Order (N = 15)",
            latex=r"\gcd(a^{r/2}-1, N)\cdot\gcd(a^{r/2}+1, N) = N \text{ for } N=15,\ a=2,\ r=4",
            description=(
                "Shor's algorithm reduces factoring to finding the order r of a modulo N. For N = 15 and a = 2 the "
                "order is 4, and the two gcds recover the factors 3 and 5."
            ),
            history=(
                "Shor (1997) showed that finding the period of modular exponentiation is solvable in polynomial "
                "time on a quantum computer. Factoring then reduces to classical number theory."
            ),
            citations=[SHOR, NIELSEN_CHUANG],
            concepts=["Shor's algorithm", "order finding", "modular arithmetic", "factoring", "gcd"],
        )

    @staticmethod
    @equation("quantum")
    def qft_unitary_n4() -> Equation:
        """The quantum Fourier transform on four amplitudes is unitary.

        Source: quantum.py
        """
        return Equation(
            id="quantum.qft_unitary_n4",
            name="Quantum Fourier Transform Is Unitary (N = 4)",
            latex=r"F_N^\dagger F_N = I,\quad F_N = \tfrac{1}{\sqrt N}\,[\omega^{jk}],\ \omega = e^{2\pi i/N},\ N=4",
            description=(
                "The discrete Fourier transform, written as a matrix of roots of unity scaled by 1 over root N, is "
                "unitary. The quantum version applies it to amplitudes, which is the period-finding step in Shor's "
                "algorithm."
            ),
            history=(
                "The discrete Fourier transform is classical. Coppersmith (1994) gave an approximate version that "
                "fits quantum circuits, and Shor (1997) used the transform to find periods."
            ),
            citations=[NIELSEN_CHUANG, SHOR],
            concepts=["quantum Fourier transform", "unitary", "roots of unity", "period finding"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all quantum computing equations."""
    return equations_for("quantum")
