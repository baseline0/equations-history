"""Typer CLI for equations-history.

Commands mirror the equation structure:
  learn autoencoder              # List all autoencoder topics
  learn autoencoder --explain    # Show all equations + narrative
  learn autoencoder encoder      # Show just encoder equation
  learn bert attention           # Show BERT attention mechanism
  learn optimizers               # List all optimizer equations
  learn regularization           # List all regularization equations
  learn loss-functions           # List all loss function equations
  learn diffusion                # List all diffusion model equations
"""

from enum import StrEnum

import typer

from equations_history.equations.autoencoders import get_all_equations as get_ae_equations
from equations_history.equations.bert import get_all_equations as get_bert_equations
from equations_history.equations.diffusion import get_all_equations as get_diff_equations
from equations_history.equations.loss_functions import get_all_equations as get_loss_equations
from equations_history.equations.optimizers import get_all_equations as get_opt_equations
from equations_history.equations.regularization import get_all_equations as get_reg_equations


class Toggle(StrEnum):
    """Explicit boolean value for a command option: `--name true` or `--name false`."""

    TRUE = "true"
    FALSE = "false"


app = typer.Typer(help="equations-history: traceable, code-grounded equation narratives for learning ML math")


@app.command()
def autoencoder(
    topic: str = typer.Option(
        ...,
        "--topic",
        help="Specific equation (encoder, decoder, mse_loss, vae_elbo, etc.), or all to list every topic",
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """Autoencoder equations: deterministic and variational."""
    equations = get_ae_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
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
    topic: str = typer.Option(
        ..., "--topic", help="Specific equation (attention, mlm, nsp, etc.), or all to list every topic"
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """BERT equations: scaled dot-product attention and masked language modeling."""
    equations = get_bert_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nBERT Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def optimizers(
    topic: str = typer.Option(
        ...,
        "--topic",
        help="Specific equation (sgd_update, momentum_update, adam_update, etc.), or all to list every topic",
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """Optimizer equations: SGD, momentum, and Adam."""
    equations = get_opt_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nOptimizer Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def regularization(
    topic: str = typer.Option(
        ...,
        "--topic",
        help="Specific equation (dropout_training, l2_regularization, batch_normalization_normalize, etc.), or all to list every topic",
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """Regularization equations: dropout, L2 penalty, and batch normalization."""
    equations = get_reg_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nRegularization Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def loss_functions(
    topic: str = typer.Option(
        ...,
        "--topic",
        help="Specific equation (cross_entropy_binary, kl_divergence, wasserstein_distance, etc.), or all to list every topic",
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """Loss function equations: cross-entropy, KL divergence, and Wasserstein distance."""
    equations = get_loss_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nLoss Function Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def diffusion(
    topic: str = typer.Option(
        ...,
        "--topic",
        help="Specific equation (forward_process_markov, reverse_process, noise_prediction_objective, etc.), or all to list every topic",
    ),
    explain: Toggle = typer.Option(
        ...,
        "--explain",
        help="true: show all equations with full narrative; false: show one topic or list them",
    ),
    citations: Toggle = typer.Option(
        ..., "--citations", help="true: include citations for each equation; false: omit them"
    ),
) -> None:
    """Diffusion model equations: forward process, reverse process, and score matching."""
    equations = get_diff_equations()

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for name, eq in equations.items():
            typer.echo(f"\n{'=' * 70}")
            typer.echo(f"Name: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            eq = equations[topic]
            typer.echo(f"\nName: {eq.name}")
            typer.echo(f"LaTeX: {eq.latex}")
            typer.echo(f"Description: {eq.description}")
            typer.echo(f"History: {eq.history}")
            if citations is Toggle.TRUE:
                typer.echo("Citations:")
                for cite in eq.citations:
                    typer.echo(f"  - {cite}")
            typer.echo(f"Source line: {eq.source_line}")
            typer.echo(f"Concepts: {', '.join(eq.concepts)}")
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo("\nDiffusion Model Equations:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


@app.command()
def list_all() -> None:
    """List all available equations across all topics."""
    typer.echo("\n" + "=" * 70)
    typer.echo("AUTOENCODERS")
    typer.echo("=" * 70)
    ae_eqs = get_ae_equations()
    for name, eq in ae_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "=" * 70)
    typer.echo("BERT")
    typer.echo("=" * 70)
    bert_eqs = get_bert_equations()
    for name, eq in bert_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "=" * 70)
    typer.echo("OPTIMIZERS")
    typer.echo("=" * 70)
    opt_eqs = get_opt_equations()
    for name, eq in opt_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "=" * 70)
    typer.echo("REGULARIZATION")
    typer.echo("=" * 70)
    reg_eqs = get_reg_equations()
    for name, eq in reg_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "=" * 70)
    typer.echo("LOSS FUNCTIONS")
    typer.echo("=" * 70)
    loss_eqs = get_loss_equations()
    for name, eq in loss_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")

    typer.echo("\n" + "=" * 70)
    typer.echo("DIFFUSION MODELS")
    typer.echo("=" * 70)
    diff_eqs = get_diff_equations()
    for name, eq in diff_eqs.items():
        typer.echo(f"\n  {name}: {eq.name}")
        typer.echo(f"    {eq.description}")


if __name__ == "__main__":
    app()
