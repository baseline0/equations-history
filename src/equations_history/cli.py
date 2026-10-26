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
  learn entropy                  # List all entropy and information equations
  learn quantum                  # List all quantum computing equations

The per-topic commands are generated from the equation registry. TOPIC_CLI holds
only the presentation for each topic (command name, headings, help text).
"""

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import typer

# Importing the package registers every topic module's equations.
import equations_history.equations  # noqa: F401
from equations_history.core import Equation
from equations_history.registry import equations_for, topics
from equations_history.timeline import ExportError, build_timeline, render
from equations_history.timeline import as_json as as_json_payload


class Toggle(StrEnum):
    """Explicit boolean value for a command option: `--name true` or `--name false`."""

    TRUE = "true"
    FALSE = "false"


@dataclass(frozen=True)
class TopicCLI:
    """How one registry topic is presented on the command line."""

    command: str
    heading: str
    banner: str
    summary: str
    topic_help: str


EXPLAIN_HELP = "true: show all equations with full narrative; false: show one topic or list them"
CITATIONS_HELP = "true: include citations for each equation; false: omit them"

# Display order: the order of the commands in --help and of the sections in list-all.
TOPIC_CLI: dict[str, TopicCLI] = {
    "autoencoders": TopicCLI(
        command="autoencoder",
        heading="Autoencoder Equations",
        banner="AUTOENCODERS",
        summary="Autoencoder equations: deterministic and variational.",
        topic_help="Specific equation (encoder, decoder, mse_loss, vae_elbo, etc.), or all to list every topic",
    ),
    "bert": TopicCLI(
        command="bert",
        heading="BERT Equations",
        banner="BERT",
        summary="BERT equations: scaled dot-product attention and masked language modeling.",
        topic_help="Specific equation (attention, mlm, nsp, etc.), or all to list every topic",
    ),
    "optimizers": TopicCLI(
        command="optimizers",
        heading="Optimizer Equations",
        banner="OPTIMIZERS",
        summary="Optimizer equations: SGD, momentum, and Adam.",
        topic_help="Specific equation (sgd_update, momentum_update, adam_update, etc.), or all to list every topic",
    ),
    "regularization": TopicCLI(
        command="regularization",
        heading="Regularization Equations",
        banner="REGULARIZATION",
        summary="Regularization equations: dropout, L2 penalty, and batch normalization.",
        topic_help="Specific equation (dropout_training, l2_regularization, batch_normalization_normalize, etc.), or all to list every topic",
    ),
    "loss_functions": TopicCLI(
        command="loss-functions",
        heading="Loss Function Equations",
        banner="LOSS FUNCTIONS",
        summary="Loss function equations: cross-entropy, KL divergence, and Wasserstein distance.",
        topic_help="Specific equation (cross_entropy_binary, kl_divergence, wasserstein_distance, etc.), or all to list every topic",
    ),
    "diffusion": TopicCLI(
        command="diffusion",
        heading="Diffusion Model Equations",
        banner="DIFFUSION MODELS",
        summary="Diffusion model equations: forward process, reverse process, and score matching.",
        topic_help="Specific equation (forward_process_markov, reverse_process, noise_prediction_objective, etc.), or all to list every topic",
    ),
    "entropy": TopicCLI(
        command="entropy",
        heading="Entropy & Information Equations",
        banner="ENTROPY & INFORMATION",
        summary="Entropy and information equations: entropy, mutual information, KL divergence, Jensen's inequality.",
        topic_help="Specific equation (entropy, conditional_entropy, joint_entropy, mutual_information, relative_entropy, jensens_inequality), or all to list every topic",
    ),
    "quantum": TopicCLI(
        command="quantum",
        heading="Quantum Computing Equations",
        banner="QUANTUM COMPUTING",
        summary="Quantum computing equations: qubit states, Bloch sphere, gates, Grover, Shor, and the QFT.",
        topic_help="Specific equation (state_normalisation, bloch_vector_x, born_rule_hadamard_plus, bell_state_from_hadamard_and_cnot, grover_two_qubits_one_iteration, shor_factor_from_order, qft_unitary_n4, etc.), or all to list every topic",
    ),
}

if set(TOPIC_CLI) != set(topics()):
    raise RuntimeError(f"TOPIC_CLI must cover exactly the registered topics: {sorted(set(TOPIC_CLI) ^ set(topics()))}")

app = typer.Typer(help="equations-history: traceable, code-grounded equation narratives for learning ML math")


def _echo_equation(eq: Equation, citations: Toggle, leading_newline: bool) -> None:
    """Print one equation's fields; citations only when requested."""
    prefix = "\n" if leading_newline else ""
    typer.echo(f"{prefix}Name: {eq.name}")
    typer.echo(f"LaTeX: {eq.latex}")
    typer.echo(f"Description: {eq.description}")
    typer.echo(f"History: {eq.history}")
    if citations is Toggle.TRUE:
        typer.echo("Citations:")
        for cite in eq.citations:
            typer.echo(f"  - {cite}")
    typer.echo(f"Source: {eq.source_label}")
    typer.echo(f"Concepts: {', '.join(eq.concepts)}")


def _show_topic(topic_key: str, topic: str, explain: Toggle, citations: Toggle) -> None:
    """Generic handler behind every per-topic command."""
    presentation = TOPIC_CLI[topic_key]
    equations = equations_for(topic_key)

    if explain is Toggle.TRUE:
        # Show all equations with full narrative
        for eq in equations.values():
            typer.echo(f"\n{'=' * 70}")
            _echo_equation(eq, citations, leading_newline=False)
    elif topic != "all":
        # Show specific equation
        if topic in equations:
            _echo_equation(equations[topic], citations, leading_newline=True)
        else:
            typer.echo(f"Unknown topic: {topic}", err=True)
            typer.echo("Available topics:", err=True)
            for name in equations:
                typer.echo(f"  - {name}", err=True)
            raise typer.Exit(1)
    else:
        # List all equations
        typer.echo(f"\n{presentation.heading}:")
        for name, eq in equations.items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    Description: {eq.description[:70]}...")


def _register_topic_command(topic_key: str, presentation: TopicCLI) -> None:
    """Add the typer command for one topic; its options and help come from TOPIC_CLI."""

    def command(
        topic: str = typer.Option(..., "--topic", help=presentation.topic_help),
        explain: Toggle = typer.Option(
            ...,
            "--explain",
            help="true: show all equations with full narrative; false: show one topic or list them",
        ),
        citations: Toggle = typer.Option(..., "--citations", help=CITATIONS_HELP),
    ) -> None:
        _show_topic(topic_key, topic, explain, citations)

    command.__doc__ = presentation.summary
    app.command(name=presentation.command)(command)


for _topic_key, _presentation in TOPIC_CLI.items():
    _register_topic_command(_topic_key, _presentation)


@app.command()
def list_all() -> None:
    """List all available equations across all topics."""
    for topic_key, presentation in TOPIC_CLI.items():
        typer.echo("\n" + "=" * 70)
        typer.echo(presentation.banner)
        typer.echo("=" * 70)
        for name, eq in equations_for(topic_key).items():
            typer.echo(f"\n  {name}: {eq.name}")
            typer.echo(f"    {eq.description}")


@app.command()
def timeline(
    export: Path = typer.Option(..., "--export", help="The knowledge export (collected.json) from tool-lit-review."),
    paper: str = typer.Option(..., "--paper", help="Comma-separated versioned arXiv ids, for example 2609.16108v1."),
    as_json: bool = typer.Option(  # typer-explicit: allow-optional: JSON output is opt-in
        False, "--json", help="Print the timeline as JSON instead of text."
    ),
) -> None:
    """Timeline of the equations collected from the chosen papers, dated by publication, unknown dates last."""
    chosen = {item.strip() for item in paper.split(",") if item.strip()}
    try:
        result = build_timeline(export, chosen)
    except (ExportError, ValueError) as error:
        typer.echo(f"ERROR {error}", err=True)
        raise typer.Exit(code=2) from error
    if as_json:
        typer.echo(json.dumps(as_json_payload(result), indent=2, ensure_ascii=False))
    else:
        typer.echo(render(result))


@app.command()
def citations(
    graph: Path = typer.Option(
        ..., "--graph", help="papers/graph.json from tool-lit-review (validated against the contract)."
    ),
    paper: str = typer.Option(..., "--paper", help="A versioned arXiv id in the graph, for example 2610.23840v1."),
) -> None:
    """Which graph papers the chosen paper cites, and which graph papers cite it. Reads only."""
    from equations_history.citations import GraphError, load_graph

    try:
        loaded = load_graph(graph)
    except GraphError as error:
        typer.echo(f"ERROR {error}", err=True)
        raise typer.Exit(code=2) from error
    if paper not in loaded.nodes:
        typer.echo(f"{paper} is not a node in {graph.name}")
        raise typer.Exit(code=1)
    typer.echo(f"cites ({len(loaded.cites(paper))}): " + (", ".join(loaded.cites(paper)) or "none in graph"))
    typer.echo(f"cited by ({len(loaded.cited_by(paper))}): " + (", ".join(loaded.cited_by(paper)) or "none in graph"))


if __name__ == "__main__":
    app()
