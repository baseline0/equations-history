"""FastAPI endpoints for equations-history.

Auto-generated from Typer CLI commands. Endpoints mirror the CLI structure:
  GET /api/equations/autoencoder/encoder
  GET /api/equations/bert/attention
  GET /api/equations?explain=true
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Dict, Optional
from equations_history.equations.autoencoders import get_all_equations as get_ae_equations
from equations_history.equations.bert import get_all_equations as get_bert_equations
from equations_history.shared_taxonomy.registry import (
    get_equation as get_taxonomy,
    get_related_equations,
    list_all_relations,
)
from equations_history.shared_taxonomy.models import (
    TaxonomyIdentifier,
    RelationshipKind,
    RelationshipStrength,
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
    source_line: int
    concepts: list[str]


class ParameterMappingResponse(BaseModel):
    """Parameter correspondence between two systems."""
    source_param: str
    target_param: str
    source_name: str
    target_name: str
    interpretation: str
    normalized_form: Optional[str] = None
    units_source: Optional[str] = None
    units_target: Optional[str] = None


class RelationshipTypeResponse(BaseModel):
    """Specification of a relationship."""
    kind: str
    definition: str
    strength: str
    formal_proof: Optional[str] = None
    formal_proof_url: Optional[str] = None
    notes: str = ""


class RelatedEquationResponse(BaseModel):
    """A related equation with mapping and relationship details."""
    target_domain: str
    target_family: str
    target_name: str
    target_full_id: str
    relationship: RelationshipTypeResponse
    parameter_mapping: Dict[str, ParameterMappingResponse]
    normalized_form_source: Optional[str] = None
    normalized_form_target: Optional[str] = None
    notes: str = ""


class TaxonomyResponse(BaseModel):
    """Taxonomic classification of an equation."""
    mathematical_form: Dict[str, Optional[str]] = Field(default_factory=dict)
    physical_role: List[str] = Field(default_factory=list)
    structural_features: List[str] = Field(default_factory=list)
    domain: str
    structural_families: List[str] = Field(default_factory=list)
    related_equations: List[RelatedEquationResponse] = Field(default_factory=list)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/equations/autoencoder", response_model=dict[str, EquationResponse])
async def list_autoencoder_equations(
    explain: bool = False,
) -> dict[str, EquationResponse]:
    """List all autoencoder equations."""
    equations = get_ae_equations()
    return {
        name: EquationResponse(
            name=eq.name,
            latex=eq.latex,
            description=eq.description,
            history=eq.history,
            citations=eq.citations,
            source_line=eq.source_line,
            concepts=eq.concepts,
        )
        for name, eq in equations.items()
    }


@app.get("/api/equations/autoencoder/{topic}", response_model=EquationResponse)
async def get_autoencoder_equation(topic: str) -> EquationResponse:
    """Get a specific autoencoder equation."""
    equations = get_ae_equations()
    if topic not in equations:
        raise HTTPException(status_code=404, detail=f"Equation {topic} not found")
    eq = equations[topic]
    return EquationResponse(
        name=eq.name,
        latex=eq.latex,
        description=eq.description,
        history=eq.history,
        citations=eq.citations,
        source_line=eq.source_line,
        concepts=eq.concepts,
    )


@app.get("/api/equations/bert", response_model=dict[str, EquationResponse])
async def list_bert_equations(
    explain: bool = False,
) -> dict[str, EquationResponse]:
    """List all BERT equations."""
    equations = get_bert_equations()
    return {
        name: EquationResponse(
            name=eq.name,
            latex=eq.latex,
            description=eq.description,
            history=eq.history,
            citations=eq.citations,
            source_line=eq.source_line,
            concepts=eq.concepts,
        )
        for name, eq in equations.items()
    }


@app.get("/api/equations/bert/{topic}", response_model=EquationResponse)
async def get_bert_equation(topic: str) -> EquationResponse:
    """Get a specific BERT equation."""
    equations = get_bert_equations()
    if topic not in equations:
        raise HTTPException(status_code=404, detail=f"Equation {topic} not found")
    eq = equations[topic]
    return EquationResponse(
        name=eq.name,
        latex=eq.latex,
        description=eq.description,
        history=eq.history,
        citations=eq.citations,
        source_line=eq.source_line,
        concepts=eq.concepts,
    )


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
    related_list: List[RelatedEquationResponse] = []
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


@app.get("/api/relations/all", response_model=List[Dict[str, str]])
async def get_all_relations_summary() -> List[Dict[str, str]]:
    """Get summary of all documented cross-domain relationships."""
    relations = list_all_relations()
    return [
        {
            "source": relation.source.full_id(),
            "target": relation.target.full_id(),
            "kind": relation.relationship.kind.value,
            "strength": relation.relationship.strength.value,
            "description": relation.relationship.definition[:200] + "..." if len(relation.relationship.definition) > 200 else relation.relationship.definition,
        }
        for relation in relations
    ]


# Serve static files (web UI) — MUST be last so API routes take precedence
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")
