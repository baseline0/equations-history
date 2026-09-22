"""Concrete taxonomy examples: mechanical oscillator ↔ RLC circuit."""

from .models import (
    TaxonomyIdentifier,
    EquationTaxonomy,
    Relation,
    RelationshipType,
    RelationshipKind,
    RelationshipStrength,
    ParameterMapping,
    MathematicalForm,
)


# ============================================================================
# Identifiers
# ============================================================================

MECHANICAL_OSCILLATOR = TaxonomyIdentifier(
    domain="mechanics",
    family="damped_oscillator",
    name="mechanical_damped_oscillator"
)

RLC_CIRCUIT = TaxonomyIdentifier(
    domain="electrical",
    family="rlc",
    name="rlc_circuit"
)


# ============================================================================
# Taxonomies
# ============================================================================

MECHANICAL_OSCILLATOR_TAXONOMY = EquationTaxonomy(
    identifier=MECHANICAL_OSCILLATOR,
    mathematical_form=MathematicalForm(
        primary="ordinary_differential_equation",
        order=2,
        linearity="linear",
        time_dependence="time_invariant",
        variables="continuous"
    ),
    physical_role=[
        "state_evolution",
        "forced",
        "dissipative"
    ],
    structural_features=[
        "energy_storage",
        "energy_dissipation",
        "input_output",
        "feedback_compatible"
    ],
    domain="mechanics",
    structural_families=[
        "LinearTimeInvariantSecondOrder",
        "DissipativeSystem",
        "PortHamiltonianSystem"
    ],
    discovered_by="Classical mechanics tradition",
    year_discovered=None,  # Ancient
    references=[
        "Newton's second law (1687)",
        "Hooke's law (1660s)",
        "Stokes drag (1845)"
    ],
    notes="Fundamental model in mechanical engineering. Foundation for understanding vibration, shock absorbers, seismic isolation."
)


RLC_CIRCUIT_TAXONOMY = EquationTaxonomy(
    identifier=RLC_CIRCUIT,
    mathematical_form=MathematicalForm(
        primary="ordinary_differential_equation",
        order=2,
        linearity="linear",
        time_dependence="time_invariant",
        variables="continuous"
    ),
    physical_role=[
        "state_evolution",
        "forced",
        "dissipative"
    ],
    structural_features=[
        "energy_storage",
        "energy_dissipation",
        "input_output",
        "feedback_compatible"
    ],
    domain="electrical",
    structural_families=[
        "LinearTimeInvariantSecondOrder",
        "DissipativeSystem",
        "PortHamiltonianSystem"
    ],
    discovered_by="Electrical circuit analysis tradition",
    year_discovered=None,
    references=[
        "Ohm's law (1827)",
        "Faraday's law (1831)",
        "Circuit analysis (19th century onward)"
    ],
    notes="Fundamental model in electrical engineering. Basis for filters, resonant circuits, oscillators."
)


# ============================================================================
# Relationship: Parameter Correspondence and State-Space Equivalence
# ============================================================================

MECH_RLC_PARAMETER_MAPPING = {
    "mass_inductance": ParameterMapping(
        source_param="m",
        target_param="L",
        source_name="mass",
        target_name="inductance",
        interpretation="Inertia (mass) corresponds to inductance; both resist change in velocity/current",
        normalized_form="Both enter as coefficient of highest-order derivative",
        units_source="kg",
        units_target="H"
    ),
    "damping_resistance": ParameterMapping(
        source_param="c",
        target_param="R",
        source_name="damping coefficient",
        target_name="resistance",
        interpretation="Mechanical damping (friction) corresponds to resistance; both dissipate energy proportional to velocity/current",
        normalized_form="Both multiplied by first derivative of state variable",
        units_source="N·s/m",
        units_target="Ω"
    ),
    "stiffness_capacitance": ParameterMapping(
        source_param="k",
        target_param="1/C",
        source_name="spring stiffness",
        target_name="inverse capacitance",
        interpretation="Spring stiffness corresponds to 1/C; both provide restoring force/voltage proportional to displacement/charge",
        normalized_form="Both enter without derivative (0th-order term)",
        units_source="N/m",
        units_target="1/F"
    ),
    "forcing_voltage": ParameterMapping(
        source_param="F(t)",
        target_param="V(t)",
        source_name="applied force",
        target_name="applied voltage",
        interpretation="External force input corresponds to voltage input",
        normalized_form="Both appear as forcing term on right-hand side",
        units_source="N",
        units_target="V"
    ),
    "displacement_charge": ParameterMapping(
        source_param="x",
        target_param="q",
        source_name="displacement",
        target_name="charge",
        interpretation="Position of mass corresponds to charge on capacitor",
        normalized_form="Both are the state variable being integrated",
        units_source="m",
        units_target="C"
    ),
    "velocity_current": ParameterMapping(
        source_param="ẋ",
        target_param="q̇ = i",
        source_name="velocity",
        target_name="current",
        interpretation="Velocity of mass corresponds to electrical current",
        normalized_form="Both are first derivative of state",
        units_source="m/s",
        units_target="A"
    ),
}


MECH_RLC_RELATION = Relation(
    source=MECHANICAL_OSCILLATOR,
    target=RLC_CIRCUIT,
    relationship=RelationshipType(
        kind=RelationshipKind.PARAMETER_CORRESPONDENCE,
        definition=(
            "Under the specified variable and parameter substitution, the mechanical damped oscillator "
            "and RLC circuit exhibit identical normalized state-space dynamics. "
            "Both can be written in the form: ξ̈ + 2ζω₀ξ̇ + ω₀²ξ = u, "
            "where ω₀² = k/m or 1/(LC), and ζ = c/(2√(km)) or R√(C/L)/2. "
            "This correspondence is structure-preserving: energy storage, dissipation, and forcing map cleanly across domains."
        ),
        strength=RelationshipStrength.PROVEN_EQUIVALENCE,
        formal_proof="math_trace.theorems.mechanical_rlc_normalized_state_space_equivalence",
        formal_proof_url="https://github.com/baseline0/math-trace/blob/main/src/DynamicalSystem.lean",
        notes="This is a canonical example of domain-independent structure. Both systems are instances of port-Hamiltonian systems."
    ),
    parameter_mapping=MECH_RLC_PARAMETER_MAPPING,
    normalized_form_source=r"m\ddot{x} + c\dot{x} + kx = F(t)",
    normalized_form_target=r"L\ddot{q} + R\dot{q} + \frac{1}{C}q = V(t)",
    visual_diagram="bond_graph_second_order_system",
    visual_diagram_url="https://example.com/bond_graph_rlc.svg",  # TODO: create this
    notes=(
        "This correspondence is one of the most important in systems theory. "
        "It demonstrates that energy-dissipative, second-order linear systems have a common abstract structure "
        "independent of physical domain. Extensions to thermal systems (RC circuits), "
        "hydraulic systems, and even quantum harmonic oscillators follow similar patterns."
    ),
    discovered_by="Systems and control theory tradition",
    year_discovered=1960,  # Approximate; the analogy is much older, but formal state-space theory developed mid-20th century
    references=[
        "Paynter, H. M. (1961). Analysis and design of engineering systems. MIT Press. (Bond graphs)",
        "Kalman, R. E., Falb, P. L., & Arbib, M. A. (1969). Topics in mathematical systems theory. McGraw-Hill. (State-space theory)",
        "van der Schaft, A. (2017). Port-Hamiltonian differential-algebraic systems. Springer. (Unified framework)",
    ]
)


# Add relations to taxonomies
MECHANICAL_OSCILLATOR_TAXONOMY.relations.append(MECH_RLC_RELATION)
RLC_CIRCUIT_TAXONOMY.relations.append(MECH_RLC_RELATION)
