"""FastAPI endpoints for equations-history.

Auto-generated from Typer CLI commands. Endpoints mirror the CLI structure:
  GET /api/equations/autoencoder/encoder
  GET /api/equations/bert/attention
  GET /api/equations?explain=true
"""

from typing import NamedTuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Importing the package registers every topic module's equations.
import equations_history.equations  # noqa: F401
from equations_history.constants import REPO_ROOT
from equations_history.core import Equation
from equations_history.registry import equations_for, topics
from equations_history.shared_taxonomy.models import (
    TaxonomyIdentifier,
)
from equations_history.shared_taxonomy.registry import (
    get_equation as get_taxonomy,
)
from equations_history.shared_taxonomy.registry import (
    list_all_relations,
)

app = FastAPI(
    title="equations-history API",
    description="Traceable, code-grounded equation narratives for learning ML math",
    version="0.1.0",
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EquationResponse(BaseModel):
    """API response for an equation."""

    name: str
    latex: str
    description: str
    history: str
    citations: list[str]
    source: str
    concepts: list[str]


class ParameterMappingResponse(BaseModel):
    """Parameter correspondence between two systems."""

    source_param: str
    target_param: str
    source_name: str
    target_name: str
    interpretation: str
    normalized_form: str | None = None
    units_source: str | None = None
    units_target: str | None = None


class RelationshipTypeResponse(BaseModel):
    """Specification of a relationship."""

    kind: str
    definition: str
    strength: str
    formal_proof: str | None = None
    formal_proof_url: str | None = None
    notes: str = ""


class RelatedEquationResponse(BaseModel):
    """A related equation with mapping and relationship details."""

    target_domain: str
    target_family: str
    target_name: str
    target_full_id: str
    relationship: RelationshipTypeResponse
    parameter_mapping: dict[str, ParameterMappingResponse]
    normalized_form_source: str | None = None
    normalized_form_target: str | None = None
    notes: str = ""


class TaxonomyResponse(BaseModel):
    """Taxonomic classification of an equation."""

    mathematical_form: dict[str, str | int | None] = Field(default_factory=dict)
    physical_role: list[str] = Field(default_factory=list)
    structural_features: list[str] = Field(default_factory=list)
    domain: str
    structural_families: list[str] = Field(default_factory=list)
    related_equations: list[RelatedEquationResponse] = Field(default_factory=list)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


class ApiRoute(NamedTuple):
    """HTTP route segment and handler naming for one registry topic."""

    segment: str
    stem: str
    label: str


# Every registered topic has routes. A topic missing here is unreachable over HTTP, and a test checks that none is.
API_ROUTES: dict[str, ApiRoute] = {
    "autoencoders": ApiRoute(segment="autoencoder", stem="autoencoder", label="autoencoder"),
    "bert": ApiRoute(segment="bert", stem="bert", label="BERT"),
    "optimizers": ApiRoute(segment="optimizers", stem="optimizer", label="optimizer"),
    "regularization": ApiRoute(segment="regularization", stem="regularization", label="regularization"),
    "loss_functions": ApiRoute(segment="loss-functions", stem="loss_function", label="loss function"),
    "diffusion": ApiRoute(segment="diffusion", stem="diffusion", label="diffusion model"),
    "entropy": ApiRoute(segment="entropy", stem="entropy", label="entropy"),
    "quantum": ApiRoute(segment="quantum", stem="quantum", label="quantum computing"),
    "biochemistry": ApiRoute(segment="biochemistry", stem="biochemistry", label="biochemistry"),
}

if not set(API_ROUTES) <= set(topics()):
    raise RuntimeError(f"API_ROUTES names unregistered topics: {sorted(set(API_ROUTES) - set(topics()))}")


def _to_response(eq: Equation) -> EquationResponse:
    """Build the API response for one equation."""
    return EquationResponse(
        name=eq.name,
        latex=eq.latex,
        description=eq.description,
        history=eq.history,
        citations=eq.citations,
        source=eq.source_label,
        concepts=eq.concepts,
    )


def _add_topic_routes(topic_key: str, route: ApiRoute) -> None:
    """Register the list and single-equation GET routes for one topic."""

    async def list_equations(explain: bool = False) -> dict[str, EquationResponse]:
        return {name: _to_response(eq) for name, eq in equations_for(topic_key).items()}

    async def get_equation(topic: str) -> EquationResponse:
        equations = equations_for(topic_key)
        if topic not in equations:
            raise HTTPException(status_code=404, detail=f"Equation {topic} not found")
        return _to_response(equations[topic])

    list_equations.__name__ = f"list_{route.stem}_equations"
    list_equations.__doc__ = f"List all {route.label} equations."
    get_equation.__name__ = f"get_{route.stem}_equation"
    get_equation.__doc__ = f"Get a specific {route.label} equation."
    app.get(f"/api/equations/{route.segment}", response_model=dict[str, EquationResponse])(list_equations)
    app.get(f"/api/equations/{route.segment}/{{topic}}", response_model=EquationResponse)(get_equation)


for _topic_key, _route in API_ROUTES.items():
    _add_topic_routes(_topic_key, _route)


# ============================================================================
# Taxonomy Endpoints (Phase 3b)
# ============================================================================


@app.get("/api/taxonomy/{domain}/{family}/{name}", response_model=TaxonomyResponse)
async def get_equation_taxonomy(domain: str, family: str, name: str) -> TaxonomyResponse:
    """Get taxonomic classification for an equation."""
    identifier = TaxonomyIdentifier(domain=domain, family=family, name=name)
    taxonomy = get_taxonomy(identifier)

    if not taxonomy:
        raise HTTPException(status_code=404, detail=f"Taxonomy not found for {identifier.full_id()}")

    # Build related equations response
    related_list: list[RelatedEquationResponse] = []
    for relation in taxonomy.relations:
        target = relation.target if relation.source.full_id() == identifier.full_id() else relation.source

        param_mappings = {
            key: ParameterMappingResponse(
                source_param=mapping.source_param,
                target_param=mapping.target_param,
                source_name=mapping.source_name,
                target_name=mapping.target_name,
                interpretation=mapping.interpretation,
                normalized_form=mapping.normalized_form,
                units_source=mapping.units_source,
                units_target=mapping.units_target,
            )
            for key, mapping in relation.parameter_mapping.items()
        }

        related_list.append(
            RelatedEquationResponse(
                target_domain=target.domain,
                target_family=target.family,
                target_name=target.name,
                target_full_id=target.full_id(),
                relationship=RelationshipTypeResponse(
                    kind=relation.relationship.kind.value,
                    definition=relation.relationship.definition,
                    strength=relation.relationship.strength.value,
                    formal_proof=relation.relationship.formal_proof,
                    formal_proof_url=relation.relationship.formal_proof_url,
                    notes=relation.relationship.notes,
                ),
                parameter_mapping=param_mappings,
                normalized_form_source=relation.normalized_form_source,
                normalized_form_target=relation.normalized_form_target,
                notes=relation.notes,
            )
        )

    return TaxonomyResponse(
        mathematical_form={
            "primary": taxonomy.mathematical_form.primary,
            "order": taxonomy.mathematical_form.order,
            "linearity": taxonomy.mathematical_form.linearity,
            "time_dependence": taxonomy.mathematical_form.time_dependence,
            "variables": taxonomy.mathematical_form.variables,
        },
        physical_role=taxonomy.physical_role,
        structural_features=taxonomy.structural_features,
        domain=taxonomy.domain,
        structural_families=taxonomy.structural_families,
        related_equations=related_list,
    )


@app.get("/api/relations/all", response_model=list[dict[str, str]])
async def get_all_relations_summary() -> list[dict[str, str]]:
    """Get summary of all documented cross-domain relationships."""
    relations = list_all_relations()
    return [
        {
            "source": relation.source.full_id(),
            "target": relation.target.full_id(),
            "kind": relation.relationship.kind.value,
            "strength": relation.relationship.strength.value,
            "description": relation.relationship.definition[:200] + "..."
            if len(relation.relationship.definition) > 200
            else relation.relationship.definition,
        }
        for relation in relations
    ]


# Serve static files (web UI) — MUST be last so API routes take precedence
web_dir = REPO_ROOT / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")
