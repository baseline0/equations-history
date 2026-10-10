"""Tests for shared_taxonomy module."""

import pytest
from equations_history.shared_taxonomy.models import (
    TaxonomyIdentifier,
    RelationshipKind,
    RelationshipStrength,
    ParameterMapping,
)
from equations_history.shared_taxonomy.examples import (
    MECHANICAL_OSCILLATOR,
    RLC_CIRCUIT,
    MECHANICAL_OSCILLATOR_TAXONOMY,
    RLC_CIRCUIT_TAXONOMY,
    MECH_RLC_RELATION,
)
from equations_history.shared_taxonomy.registry import (
    get_equation,
    get_relations,
    get_related_equations,
    list_equations,
    list_equations_by_domain,
    list_all_relations,
)


class TestTaxonomyIdentifier:
    """Test equation identifiers."""

    def test_identifier_full_id(self) -> None:
        """Test full_id() generates correct string."""
        assert MECHANICAL_OSCILLATOR.full_id() == "mechanics.damped_oscillator.mechanical_damped_oscillator"
        assert RLC_CIRCUIT.full_id() == "electrical.rlc.rlc_circuit"

    def test_identifier_string_representation(self) -> None:
        """Test string representation."""
        assert str(MECHANICAL_OSCILLATOR) == MECHANICAL_OSCILLATOR.full_id()


class TestParameterMapping:
    """Test parameter correspondences."""

    def test_mapping_completeness(self) -> None:
        """Test that mapping has required fields."""
        mapping = MECH_RLC_RELATION.parameter_mapping["mass_inductance"]
        assert mapping.source_param == "m"
        assert mapping.target_param == "L"
        assert mapping.source_name == "mass"
        assert mapping.target_name == "inductance"
        assert mapping.interpretation
        assert mapping.normalized_form

    def test_all_mappings_present(self) -> None:
        """Test that all expected mappings exist."""
        expected_keys = {
            "mass_inductance",
            "damping_resistance",
            "stiffness_capacitance",
            "forcing_voltage",
            "displacement_charge",
            "velocity_current",
        }
        assert set(MECH_RLC_RELATION.parameter_mapping.keys()) == expected_keys


class TestRelationship:
    """Test relationships between equations."""

    def test_relationship_kind(self) -> None:
        """Test relationship kind is correctly specified."""
        assert MECH_RLC_RELATION.relationship.kind == RelationshipKind.PARAMETER_CORRESPONDENCE

    def test_relationship_strength(self) -> None:
        """Test relationship strength reflects level of formalization."""
        assert MECH_RLC_RELATION.relationship.strength == RelationshipStrength.PROVEN_EQUIVALENCE

    def test_relationship_formal_proof_reference(self) -> None:
        """Test that formal proof is referenced."""
        assert MECH_RLC_RELATION.relationship.formal_proof
        assert "mechanical_rlc" in MECH_RLC_RELATION.relationship.formal_proof.lower()

    def test_normalized_forms_present(self) -> None:
        """Test that normalized forms are documented."""
        assert MECH_RLC_RELATION.normalized_form_source
        assert MECH_RLC_RELATION.normalized_form_target


class TestEquationTaxonomy:
    """Test equation taxonomies."""

    def test_mechanical_taxonomy_classification(self) -> None:
        """Test mechanical oscillator taxonomy."""
        tax = MECHANICAL_OSCILLATOR_TAXONOMY
        assert tax.domain == "mechanics"
        assert tax.mathematical_form.order == 2
        assert tax.mathematical_form.linearity == "linear"
        assert "energy_storage" in tax.structural_features
        assert "energy_dissipation" in tax.structural_features

    def test_rlc_taxonomy_classification(self) -> None:
        """Test RLC circuit taxonomy."""
        tax = RLC_CIRCUIT_TAXONOMY
        assert tax.domain == "electrical"
        assert tax.mathematical_form.order == 2
        assert tax.mathematical_form.linearity == "linear"
        assert "energy_storage" in tax.structural_features

    def test_taxonomies_in_same_families(self) -> None:
        """Test that both equations are in common structural families."""
        mech_families = set(MECHANICAL_OSCILLATOR_TAXONOMY.structural_families)
        rlc_families = set(RLC_CIRCUIT_TAXONOMY.structural_families)
        common = mech_families & rlc_families
        assert "LinearTimeInvariantSecondOrder" in common
        assert "DissipativeSystem" in common

    def test_relations_bidirectional(self) -> None:
        """Test that relations are recorded in both taxonomies."""
        mech_related = get_related_equations(MECHANICAL_OSCILLATOR)
        rlc_related = get_related_equations(RLC_CIRCUIT)
        assert RLC_CIRCUIT in mech_related
        assert MECHANICAL_OSCILLATOR in rlc_related

    def test_get_relations_by_kind(self) -> None:
        """Test filtering relations by kind."""
        tax = MECHANICAL_OSCILLATOR_TAXONOMY
        param_corr = tax.get_relations_by_kind(RelationshipKind.PARAMETER_CORRESPONDENCE)
        assert len(param_corr) > 0
        assert MECH_RLC_RELATION in param_corr

    def test_get_relations_by_strength(self) -> None:
        """Test filtering relations by strength."""
        tax = MECHANICAL_OSCILLATOR_TAXONOMY
        proven = tax.get_relations_by_strength(RelationshipStrength.PROVEN_EQUIVALENCE)
        assert len(proven) > 0
        assert MECH_RLC_RELATION in proven


class TestRegistry:
    """Test the equation registry."""

    def test_get_equation(self) -> None:
        """Test retrieving equation from registry."""
        mech = get_equation(MECHANICAL_OSCILLATOR)
        assert mech is not None
        assert mech.domain == "mechanics"

    def test_get_equation_not_found(self) -> None:
        """Test that missing equation returns None."""
        fake_id = TaxonomyIdentifier("unknown", "unknown", "unknown")
        assert get_equation(fake_id) is None

    def test_get_relations(self) -> None:
        """Test retrieving relations for an equation."""
        relations = get_relations(MECHANICAL_OSCILLATOR)
        assert len(relations) > 0
        assert MECH_RLC_RELATION in relations

    def test_list_equations(self) -> None:
        """Test listing all equations."""
        equations = list_equations()
        assert len(equations) >= 2
        assert MECHANICAL_OSCILLATOR_TAXONOMY in equations
        assert RLC_CIRCUIT_TAXONOMY in equations

    def test_list_equations_by_domain(self) -> None:
        """Test filtering equations by domain."""
        mech_eqs = list_equations_by_domain("mechanics")
        assert len(mech_eqs) >= 1
        assert MECHANICAL_OSCILLATOR_TAXONOMY in mech_eqs

        elec_eqs = list_equations_by_domain("electrical")
        assert len(elec_eqs) >= 1
        assert RLC_CIRCUIT_TAXONOMY in elec_eqs

    def test_list_all_relations(self) -> None:
        """Test listing all relations."""
        relations = list_all_relations()
        assert len(relations) > 0
        # The relation should appear in the list (possibly twice if bidirectional)
        assert any(r.source == MECHANICAL_OSCILLATOR and r.target == RLC_CIRCUIT for r in relations)
