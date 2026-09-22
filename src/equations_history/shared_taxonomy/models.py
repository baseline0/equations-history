"""Core data models for equation taxonomy.

Provides stable, language-agnostic representations of:
- Equation identities
- Structural families
- Relationship types and strengths
- Parameter mappings
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum


class RelationshipKind(str, Enum):
    """Vocabulary of relationship types between equations."""
    ANALOGY = "analogy"  # Useful correspondence; not formally proven
    PARAMETER_CORRESPONDENCE = "parameter_correspondence"  # Named quantities occupy similar roles
    MODEL_EQUIVALENCE = "model_equivalence"  # Same behavior after change of variables
    ISOMORPHISM = "isomorphism"  # Invertible, structure-preserving map (use sparingly)
    SIMULATION = "simulation"  # One system maps into another; not necessarily invertible
    SHARED_STRUCTURE = "shared_structure"  # Both instantiate a more abstract model
    HISTORICAL_RELATION = "historical_relation"  # One influenced or generalized another
    SHARED_HAMILTONIAN_PATTERN = "shared_hamiltonian_pattern"  # Common energy structure


class RelationshipStrength(str, Enum):
    """How rigorously the relationship has been established."""
    INFORMAL = "informal"  # Intuitive observation
    STRUCTURAL = "structural"  # Mathematically described but not formally proven
    PROVEN_EQUIVALENCE = "proven_equivalence"  # Formal theorem in Lean or similar


@dataclass
class TaxonomyIdentifier:
    """Globally-scoped, stable identifier for an equation."""
    domain: str  # "mechanics", "electrical", "thermal", "quantum"
    family: str  # "damped_oscillator", "rlc_circuit", "heat_diffusion"
    name: str    # Full name: "mechanical_damped_oscillator"

    def full_id(self) -> str:
        """Canonical string representation."""
        return f"{self.domain}.{self.family}.{self.name}"

    def __str__(self) -> str:
        return self.full_id()


@dataclass
class StructuralFamily:
    """An abstract mathematical pattern that multiple equations instantiate."""
    name: str  # "LinearTimeInvariantSecondOrder"
    description: str  # Plain-language description
    state_space_form: str  # LaTeX: "ẋ = Ax + Bu, y = Cx + Du"
    examples: List[TaxonomyIdentifier] = field(default_factory=list)
    lean_definition: Optional[str] = None  # Reference: "math_trace.DynamicalSystem.LinearTISecondOrder"
    notes: str = ""


@dataclass
class ParameterMapping:
    """Correspondence between a parameter in one system and another."""
    source_param: str  # e.g., "m"
    target_param: str  # e.g., "L"
    source_name: str  # e.g., "mass"
    target_name: str  # e.g., "inductance"
    interpretation: str  # e.g., "Inertia (mass) corresponds to inductance"
    normalized_form: Optional[str] = None  # e.g., "Both enter as coefficient of second derivative"
    units_source: Optional[str] = None  # e.g., "kg"
    units_target: Optional[str] = None  # e.g., "H"


@dataclass
class RelationshipType:
    """Specification of a relationship between two equations."""
    kind: RelationshipKind
    definition: str  # Plain-text or mathematical description
    strength: RelationshipStrength
    formal_proof: Optional[str] = None  # Reference: "math_trace.theorems.mechanical_rlc_equivalence"
    formal_proof_url: Optional[str] = None  # URL to GitHub, Lean4 docs, etc.
    notes: str = ""


@dataclass
class Relation:
    """A documented relationship between two equations across domains."""
    source: TaxonomyIdentifier
    target: TaxonomyIdentifier
    relationship: RelationshipType
    parameter_mapping: Dict[str, ParameterMapping] = field(default_factory=dict)

    # Normalization
    normalized_form_source: Optional[str] = None  # LaTeX of source in normalized form
    normalized_form_target: Optional[str] = None  # LaTeX of target in normalized form

    # Visualization and reference
    visual_diagram: Optional[str] = None  # "bond_graph_second_order", etc.
    visual_diagram_url: Optional[str] = None  # URL to asset or inline SVG

    # Metadata
    notes: str = ""
    discovered_by: Optional[str] = None  # Historical credit
    year_discovered: Optional[int] = None
    references: List[str] = field(default_factory=list)  # Citations


@dataclass
class MathematicalForm:
    """Classification by mathematical structure."""
    primary: str  # "ordinary_differential_equation", "algebraic", "integral"
    order: Optional[int] = None  # For ODE/PDE: order
    linearity: Optional[str] = None  # "linear", "nonlinear", "quasilinear"
    time_dependence: Optional[str] = None  # "time_invariant", "time_varying"
    variables: Optional[str] = None  # "continuous", "discrete", "hybrid"


@dataclass
class EquationTaxonomy:
    """Complete taxonomic classification of an equation."""
    identifier: TaxonomyIdentifier

    # Structural classification
    mathematical_form: MathematicalForm
    physical_role: List[str] = field(default_factory=list)  # "state_evolution", "constitutive", "constraint", "conservation"
    structural_features: List[str] = field(default_factory=list)  # "energy_storage", "dissipation", "input_output", "feedback_compatible"

    # Domain and family
    domain: str = ""
    structural_families: List[str] = field(default_factory=list)  # Which abstract families this instantiates

    # Cross-domain relationships
    relations: List[Relation] = field(default_factory=list)

    # Metadata
    discovered_by: Optional[str] = None
    year_discovered: Optional[int] = None
    references: List[str] = field(default_factory=list)
    notes: str = ""

    def get_relations_by_kind(self, kind: RelationshipKind) -> List[Relation]:
        """Find all relations of a specific kind."""
        return [r for r in self.relations if r.relationship.kind == kind]

    def get_relations_by_strength(self, strength: RelationshipStrength) -> List[Relation]:
        """Find all relations with a specific strength."""
        return [r for r in self.relations if r.relationship.strength == strength]
