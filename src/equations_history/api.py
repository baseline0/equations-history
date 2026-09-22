"""FastAPI endpoints for equations-history.

Auto-generated from Typer CLI commands. Endpoints mirror the CLI structure:
  GET /api/equations/autoencoder/encoder
  GET /api/equations/bert/attention
  GET /api/equations?explain=true
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from equations_history.equations.autoencoders import get_all_equations as get_ae_equations
from equations_history.equations.bert import get_all_equations as get_bert_equations

app = FastAPI(
    title="equations-history API",
    description="Traceable, code-grounded equation narratives for learning ML math",
    version="0.1.0",
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
