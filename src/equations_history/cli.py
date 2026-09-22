"""Typer CLI for equations-history.

Commands mirror the equation structure:
  learn autoencoder              # List all autoencoder topics
  learn autoencoder --explain    # Show all equations + narrative
  learn autoencoder encoder      # Show just encoder equation
  learn bert attention           # Show BERT attention mechanism
"""

import typer
from typing import Optional
from equations_history.equations.autoencoders import get_all_equations as get_ae_equations
from equations_history.equations.bert import get_all_equations as get_bert_equations

app = typer.Typer(help="equations-history: traceable, code-grounded equation narratives for learning ML math")


@app.command()
def autoencoder(
    topic: Optional[str] = typer.Argument(None, help="Specific equation (encoder, decoder, mse_loss, vae_elbo, etc.)"),
    explain: bool = typer.Option(False, "--explain", help="Show all equations with full narrative"),
    citations: bool = typer.Option(False, "--citations", help="Include citations for each equation"),
) -> None:
    """Autoencoder equations: deterministic and variational."""
    equations = get_ae_equations()

    if explain:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'='*70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic:
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations.keys():
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nAutoencoder Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def bert(
    topic: Optional[str] = typer.Argument(None, help="Specific equation (attention, mlm, nsp, etc.)"),
    explain: bool = typer.Option(False, "--explain", help="Show all equations with full narrative"),
    citations: bool = typer.Option(False, "--citations", help="Include citations for each equation"),
) -> None:
    """BERT equations: scaled dot-product attention and masked language modeling."""
    equations = get_bert_equations()

    if explain:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'='*70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic:
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations.keys():
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nBERT Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def list_all() -> None:
    """List all available equations across all topics."""
    typer.echo("\n" + "="*70)
    typer.echo("AUTOENCODERS")
    typer.echo("="*70)
    ae_eqs = get_ae_equations()
    for name, eq in ae_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "="*70)
    typer.echo("BERT")
    typer.echo("="*70)
    bert_eqs = get_bert_equations()
    for name, eq in bert_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")


if __name__ == "__main__":
    app()
