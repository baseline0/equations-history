"""Registry: central lookup for equation taxonomies and relationships."""

from .examples import (
    MECHANICAL_OSCILLATOR,
    MECHANICAL_OSCILLATOR_TAXONOMY,
    RLC_CIRCUIT,
    RLC_CIRCUIT_TAXONOMY,
)
from .models import EquationTaxonomy, Relation, TaxonomyIdentifier

# Central registry: all known taxonomies indexed by full identifier
EQUATION_REGISTRY: dict[str, EquationTaxonomy] = {
    MECHANICAL_OSCILLATOR.full_id(): MECHANICAL_OSCILLATOR_TAXONOMY,
    RLC_CIRCUIT.full_id(): RLC_CIRCUIT_TAXONOMY,
}


def get_equation(identifier: TaxonomyIdentifier) -> EquationTaxonomy | None:
    """Retrieve taxonomy for an equation by identifier."""
    return EQUATION_REGISTRY.get(identifier.full_id())


def get_relations(identifier: TaxonomyIdentifier) -> list[Relation]:
    """Get all relations for an equation."""
    taxonomy = get_equation(identifier)
    return taxonomy.relations if taxonomy else []


def get_related_equations(identifier: TaxonomyIdentifier) -> list[TaxonomyIdentifier]:
    """Get identifiers of equations related to the given one."""
    relations = get_relations(identifier)
    related = []
    for relation in relations:
        if relation.source.full_id() == identifier.full_id():
            related.append(relation.target)
        elif relation.target.full_id() == identifier.full_id():
            related.append(relation.source)
    return related


def register_equation(taxonomy: EquationTaxonomy) -> None:
    """Register a new equation taxonomy."""
    EQUATION_REGISTRY[taxonomy.identifier.full_id()] = taxonomy


def unregister_equation(identifier: TaxonomyIdentifier) -> None:
    """Unregister an equation taxonomy."""
    EQUATION_REGISTRY.pop(identifier.full_id(), None)


def list_equations() -> list[EquationTaxonomy]:
    """List all registered equations."""
    return list(EQUATION_REGISTRY.values())


def list_equations_by_domain(domain: str) -> list[EquationTaxonomy]:
    """List all equations in a specific domain."""
    return [tax for tax in EQUATION_REGISTRY.values() if tax.domain == domain]


def list_equations_by_family(family: str) -> list[EquationTaxonomy]:
    """List all equations in a specific family."""
    return [tax for tax in EQUATION_REGISTRY.values() if tax.identifier.family == family]


def list_all_relations() -> list[Relation]:
    """List all documented cross-domain relationships."""
    relations = []
    for taxonomy in EQUATION_REGISTRY.values():
        relations.extend(taxonomy.relations)
    return relations


def find_shortest_path(
    start: TaxonomyIdentifier, end: TaxonomyIdentifier, max_depth: int = 3
) -> list[TaxonomyIdentifier] | None:
    """
    Find shortest path of relationships between two equations.
    Uses breadth-first search.
    """
    from collections import deque

    if start.full_id() == end.full_id():
        return [start]

    visited = {start.full_id()}
    queue = deque([(start, [start])])

    while queue:
        current, path = queue.popleft()

        if len(path) > max_depth:
            continue

        related = get_related_equations(current)
        for next_id in related:
            if next_id.full_id() == end.full_id():
                return [*path, next_id]

            if next_id.full_id() not in visited:
                visited.add(next_id.full_id())
                queue.append((next_id, [*path, next_id]))

    return None
