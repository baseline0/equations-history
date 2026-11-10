"""Tests for VerificationStatus enum and verification framework."""

import pytest

from equations_history.verification import VerificationStatus


class TestVerificationStatusEnum:
    """Verify VerificationStatus enum is properly defined."""

    def test_all_six_statuses_exist(self) -> None:
        """All six verification statuses are defined."""
        expected_statuses = {
            "SOURCE_CITED",
            "TRANSCRIPTION_VERIFIED",
            "SYMBOLIC_EQUIVALENT",
            "FORMALLY_VERIFIED",
            "HISTORICAL_INTERPRETATION",
            "VISUAL_VERIFIED",
        }
        actual_statuses = {member.name for member in VerificationStatus}
        assert actual_statuses == expected_statuses

    def test_status_count(self) -> None:
        """Exactly six verification statuses."""
        assert len(list(VerificationStatus)) == 6

    def test_statuses_are_unique(self) -> None:
        """Each status has a unique value."""
        values = [member.value for member in VerificationStatus]
        assert len(values) == len(set(values))

    def test_status_membership(self) -> None:
        """Can check membership of statuses."""
        assert VerificationStatus.SOURCE_CITED in VerificationStatus
        assert VerificationStatus.FORMALLY_VERIFIED in VerificationStatus

    def test_status_equality(self) -> None:
        """Equality comparison works."""
        status = VerificationStatus.SOURCE_CITED
        assert status == VerificationStatus.SOURCE_CITED
        assert status != VerificationStatus.TRANSCRIPTION_VERIFIED

    def test_status_name_attribute(self) -> None:
        """Each status has correct name."""
        assert VerificationStatus.SOURCE_CITED.name == "SOURCE_CITED"
        assert VerificationStatus.FORMALLY_VERIFIED.name == "FORMALLY_VERIFIED"

    def test_status_value_attribute(self) -> None:
        """Each status has an auto-generated value."""
        # auto() generates unique values starting from 1
        values = [member.value for member in VerificationStatus]
        # Just check they're distinct integers
        assert all(isinstance(v, int) for v in values)
        assert len(set(values)) == 6

    def test_status_can_be_iterated(self) -> None:
        """Can iterate over all statuses."""
        statuses = list(VerificationStatus)
        assert len(statuses) == 6
        assert all(isinstance(s, VerificationStatus) for s in statuses)

    def test_status_has_docstring(self) -> None:
        """Each status has a docstring explaining its meaning."""
        for status in VerificationStatus:
            assert status.__doc__ is not None
            assert len(status.__doc__.strip()) > 0

    def test_source_cited_exists(self) -> None:
        """SOURCE_CITED status is available."""
        assert hasattr(VerificationStatus, "SOURCE_CITED")
        assert VerificationStatus.SOURCE_CITED.name == "SOURCE_CITED"

    def test_transcription_verified_exists(self) -> None:
        """TRANSCRIPTION_VERIFIED status is available."""
        assert hasattr(VerificationStatus, "TRANSCRIPTION_VERIFIED")
        assert VerificationStatus.TRANSCRIPTION_VERIFIED.name == "TRANSCRIPTION_VERIFIED"

    def test_symbolic_equivalent_exists(self) -> None:
        """SYMBOLIC_EQUIVALENT status is available."""
        assert hasattr(VerificationStatus, "SYMBOLIC_EQUIVALENT")
        assert VerificationStatus.SYMBOLIC_EQUIVALENT.name == "SYMBOLIC_EQUIVALENT"

    def test_formally_verified_exists(self) -> None:
        """FORMALLY_VERIFIED status is available."""
        assert hasattr(VerificationStatus, "FORMALLY_VERIFIED")
        assert VerificationStatus.FORMALLY_VERIFIED.name == "FORMALLY_VERIFIED"

    def test_historical_interpretation_exists(self) -> None:
        """HISTORICAL_INTERPRETATION status is available."""
        assert hasattr(VerificationStatus, "HISTORICAL_INTERPRETATION")
        assert VerificationStatus.HISTORICAL_INTERPRETATION.name == "HISTORICAL_INTERPRETATION"

    def test_visual_verified_exists(self) -> None:
        """VISUAL_VERIFIED status is available."""
        assert hasattr(VerificationStatus, "VISUAL_VERIFIED")
        assert VerificationStatus.VISUAL_VERIFIED.name == "VISUAL_VERIFIED"

    def test_status_can_be_used_in_set(self) -> None:
        """Statuses can be added to sets (hashable)."""
        status_set = {
            VerificationStatus.SOURCE_CITED,
            VerificationStatus.FORMALLY_VERIFIED,
        }
        assert len(status_set) == 2
        assert VerificationStatus.SOURCE_CITED in status_set

    def test_status_can_be_used_in_dict(self) -> None:
        """Statuses can be used as dict keys."""
        status_dict = {
            VerificationStatus.SOURCE_CITED: "equation appears in cited work",
            VerificationStatus.FORMALLY_VERIFIED: "lean theorem proven",
        }
        assert status_dict[VerificationStatus.SOURCE_CITED] == "equation appears in cited work"

    def test_all_statuses_documented_in_docstring(self) -> None:
        """The module docstring mentions all six statuses."""
        from equations_history import verification

        module_doc = verification.__doc__
        assert module_doc is not None
        # Check that all six status names appear in the module docstring
        assert "SOURCE_CITED" in module_doc or "source_cited" in module_doc
        assert "TRANSCRIPTION_VERIFIED" in module_doc or "transcription_verified" in module_doc
        assert "SYMBOLIC_EQUIVALENT" in module_doc or "symbolic_equivalent" in module_doc
        assert "FORMALLY_VERIFIED" in module_doc or "formally_verified" in module_doc
        assert "HISTORICAL_INTERPRETATION" in module_doc or "historical_interpretation" in module_doc
        assert "VISUAL_VERIFIED" in module_doc or "visual_verified" in module_doc

    def test_status_comparison_inequality(self) -> None:
        """Inequality comparison works for different statuses."""
        assert VerificationStatus.SOURCE_CITED != VerificationStatus.FORMALLY_VERIFIED

    def test_enum_is_immutable(self) -> None:
        """Enum members cannot be modified after creation."""
        status = VerificationStatus.SOURCE_CITED
        with pytest.raises(AttributeError):
            status.value = 999  # type: ignore


class TestVerificationStatusContract:
    """Verify the enum meets the contract specified in AGMAI-READY.md."""

    def test_enum_covers_all_verification_types(self) -> None:
        """Enum includes all six types from AGMAI-READY.md § Verification Vocabulary."""
        # Directly from AGMAI-READY.md lines 136-143:
        # | source_cited | ...
        # | transcription_verified | ...
        # | symbolic_equivalent | ...
        # | formally_verified | ...
        # | historical_interpretation | ...
        # | visual_verified | ...
        types = {
            VerificationStatus.SOURCE_CITED,
            VerificationStatus.TRANSCRIPTION_VERIFIED,
            VerificationStatus.SYMBOLIC_EQUIVALENT,
            VerificationStatus.FORMALLY_VERIFIED,
            VerificationStatus.HISTORICAL_INTERPRETATION,
            VerificationStatus.VISUAL_VERIFIED,
        }
        assert len(types) == 6

    def test_source_cited_documented(self) -> None:
        """SOURCE_CITED status is defined and accessible."""
        # Verify the status exists and can be accessed
        assert hasattr(VerificationStatus, "SOURCE_CITED")
        status = VerificationStatus.SOURCE_CITED
        assert status is not None
        assert status.name == "SOURCE_CITED"

    def test_formally_verified_documented(self) -> None:
        """FORMALLY_VERIFIED status is defined and accessible."""
        # Verify the status exists and can be accessed
        assert hasattr(VerificationStatus, "FORMALLY_VERIFIED")
        status = VerificationStatus.FORMALLY_VERIFIED
        assert status is not None
        assert status.name == "FORMALLY_VERIFIED"

    def test_symbolic_equivalent_documented(self) -> None:
        """SYMBOLIC_EQUIVALENT status is defined and accessible."""
        # Verify the status exists and can be accessed
        assert hasattr(VerificationStatus, "SYMBOLIC_EQUIVALENT")
        status = VerificationStatus.SYMBOLIC_EQUIVALENT
        assert status is not None
        assert status.name == "SYMBOLIC_EQUIVALENT"

    def test_contract_specifies_no_hybrid_status(self) -> None:
        """Statuses are independent; no single 'verified' status combining all."""
        # The contract explicitly lists six independent categories.
        # Confirm there is no combined "VERIFIED" status.
        status_names = {s.name for s in VerificationStatus}
        assert "VERIFIED" not in status_names
        # All six should be present separately
        assert len(status_names) == 6
