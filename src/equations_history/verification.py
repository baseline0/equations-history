"""Verification status for equations.

Specification Map:
- VerificationStatus: Enum of six verification categories for equation records (source: AGMAI-READY.md § Verification Vocabulary)

Each equation may have multiple verification statuses that independently document how it was verified:
- source_cited: Equation appears in cited work
- transcription_verified: Equation faithfully transcribed from source
- symbolic_equivalent: Modern form algebraically equivalent to original
- formally_verified: Lean theorem proven under stated assumptions
- historical_interpretation: Human-curated claim about significance/adoption (with confidence level)
- visual_verified: Interactive visualization matches mathematical claim
"""

from enum import Enum, auto


class VerificationStatus(Enum):
    """Verification categories for equation records.

    Each status independently documents a different kind of verification claim.
    An equation may have multiple statuses; they are not mutually exclusive.

    Reference: AGMAI-READY.md § Verification Vocabulary (contract v1.0, Sep 22 2026)
    """

    SOURCE_CITED = auto()
    """Equation appears in cited work with full bibliographic reference (authors, year, title, DOI/URL).

    Example: "Michaelis-Menten equation (1913), equation (2) in original paper"
    """

    TRANSCRIPTION_VERIFIED = auto()
    """Equation faithfully transcribed from cited source; manual check confirms notation matches original.

    This verifies fidelity to the source, not whether the source is correct.
    Example: "Manual check: modern form matches original notation exactly; Briggs-Haldane (1925)"
    """

    SYMBOLIC_EQUIVALENT = auto()
    """Modern form is algebraically equivalent to original under stated conditions.

    Transformation steps have been verified (may be by hand or by SymPy).
    Example: "Proven: F=ma ⟺ d(mv)/dt = F under constant m"
    """

    FORMALLY_VERIFIED = auto()
    """Lean theorem proven under explicitly stated assumptions.

    The Lean proof validates mathematical equivalence in a formal system, not empirical adequacy.
    Example: "Lean: MechanicalOscillator.energyEquals(RLCCircuit.energy) under parameter mapping"
    """

    HISTORICAL_INTERPRETATION = auto()
    """Human-curated claim about significance, adoption, or historical impact.

    These are interpretations, not formal claims. Each comes with a confidence level
    and explicit source(s).
    Example: "This formulation became the standard post-1970 based on textbook adoption survey"
    """

    VISUAL_VERIFIED = auto()
    """Interactive visualization matches mathematical claim.

    Visual verification provides a different kind of evidence: that an interactive
    demo (heatmap, phase portrait, slider) correctly represents the mathematics.
    Example: "Latent space plot confirms VAE KL divergence decay behavior"
    """
