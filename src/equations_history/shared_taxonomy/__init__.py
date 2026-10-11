"""Shared taxonomy: stable, neutral identifiers and relationships for equations.

This package provides a language-agnostic data model for:
- Equation identities (domain + family + name)
- Structural families (abstract mathematical patterns)
- Relationships between equations (with precise definitions)
- Parameter correspondences (which variables map to which)

Used by:
- equations-history: to display "related equations" and parameter mappings
- math-trace: to ground formal theorems in shared identifiers
- Future tools: to reason about structural equivalence across domains
"""

from .models import (
    ParameterMapping,
    Relation,
    RelationshipType,
    StructuralFamily,
    TaxonomyIdentifier,
)
from .registry import EQUATION_REGISTRY, get_equation, get_relations

__all__ = [
    "TaxonomyIdentifier",
    "StructuralFamily",
    "RelationshipType",
    "ParameterMapping",
    "Relation",
    "get_equation",
    "get_relations",
    "EQUATION_REGISTRY",
]
