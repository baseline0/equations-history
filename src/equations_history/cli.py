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
  learn biochemistry             # List all enzyme-kinetics equations (from math-trace)

The per-topic commands are generated from the equation registry. TOPIC_CLI holds
only the presentation for each topic (command name, headings, help text).
"""

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import typer

# Importing the package registers every topic module's equations.
import equations_history.equations  # noqa: F401
from equations_history.core import Equation
from equations_history.formula_catalog import CatalogError, load_catalog, load_narratives
from equations_history.formula_record import AssemblyError, assemble_record, check_record, public_view
from equations_history.paper_store import PaperStore
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
    "biochemistry": TopicCLI(
        command="biochemistry",
        heading="Biochemistry Equations",
        banner="BIOCHEMISTRY",
        summary="Enzyme kinetics equations from math-trace: Michaelis-Menten, V_max, K_m, k_cat, and k_cat/K_m.",
        topic_help="Specific equation (michaelis_menten, max_velocity, michaelis_constant, enzyme_mechanism, turnover_number, specificity), or all to list every topic",
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


record_app = typer.Typer(help="Formula records (formula-record/1): check them, and write the public view.")
app.add_typer(record_app, name="record")


def _read_record(path: Path) -> dict[str, Any]:
    """The JSON object in ``path``. Exits with code 2 when the file is unreadable or not an object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        typer.echo(f"ERROR {path.name}: cannot read JSON: {error}", err=True)
        raise typer.Exit(code=2) from error
    if not isinstance(data, dict):
        typer.echo(f"ERROR {path.name}: a formula record is a JSON object", err=True)
        raise typer.Exit(code=2)
    return data


@record_app.command("validate")
def record_validate(
    path: Path = typer.Option(
        ..., "--path", help="A formula record, for example records/navier-stokes-momentum-3d.json."
    ),
    paper_store: Path = typer.Option(
        ..., "--paper-store", help="The paper-store root, for example /home/mark/paper-store."
    ),
) -> None:
    """Check a formula record against the contract, its units and the paper store. Exits 1 with every problem found."""
    problems = check_record(_read_record(path), PaperStore(paper_store))
    for problem in problems:
        typer.echo(f"{path.name}: {problem}")
    if problems:
        raise typer.Exit(code=1)
    typer.echo(f"{path.name}: valid")


@record_app.command("public")
def record_public(
    path: Path = typer.Option(..., "--path", help="A formula record to reduce to its public fields."),
    paper_store: Path = typer.Option(
        ..., "--paper-store", help="The paper-store root, for example /home/mark/paper-store."
    ),
    out: Path = typer.Option(..., "--out", help="Where to write the public view, as JSON."),
) -> None:
    """Write the public view of a valid formula record. A record with problems is refused and nothing is written."""
    record = _read_record(path)
    problems = check_record(record, PaperStore(paper_store))
    if problems:
        for problem in problems:
            typer.echo(f"{path.name}: {problem}", err=True)
        raise typer.Exit(code=1)
    out.write_text(json.dumps(public_view(record), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    typer.echo(f"wrote {out}")


def _assemble_to_file(
    catalog: Path,
    narrative: Path,
    formula: str,
    record_id: str,
    source_file: str,
    paper_store: Path,
    literature: dict[str, str] | None,
    out: Path,
) -> None:
    """Assemble one formula record and write it. Exits 2 when the formula is missing, 1 when it cannot be assembled."""
    try:
        entries = load_catalog(catalog)
        narratives = load_narratives(narrative)
        if formula not in entries or formula not in narratives:
            typer.echo(f"ERROR {formula!r} is not in both {catalog.name} and {narrative.name}", err=True)
            raise typer.Exit(code=2)
        record = assemble_record(
            record_id,
            entries[formula],
            narratives[formula],
            source_file=source_file,
            store=PaperStore(paper_store),
            literature=literature,
        )
    except (CatalogError, AssemblyError) as error:
        typer.echo(f"ERROR {error}", err=True)
        raise typer.Exit(code=1) from error
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    typer.echo(f"wrote {out}")


@record_app.command("assemble")
def record_assemble(
    catalog: Path = typer.Option(..., "--catalog", help="A math-trace equations.json snapshot."),
    narrative: Path = typer.Option(..., "--narrative", help="The narrative JSON for the same topic."),
    formula: str = typer.Option(
        ..., "--formula", help="The formula's key in the catalog, for example michaelis_menten."
    ),
    record_id: str = typer.Option(..., "--id", help="The record's slug, for example michaelis-menten."),
    source_file: str = typer.Option(
        ...,
        "--source-file",
        help="The template's model.py path in math-trace, for example templates/biochemistry/src/model.py.",
    ),
    paper_store: Path = typer.Option(
        ..., "--paper-store", help="The paper-store root, for example /home/mark/paper-store."
    ),
    out: Path = typer.Option(..., "--out", help="Where to write the formula record, as JSON."),
) -> None:
    """Assemble a code-only formula record, and check it against the paper store."""
    _assemble_to_file(catalog, narrative, formula, record_id, source_file, paper_store, None, out)


@record_app.command("assemble-cited")
def record_assemble_cited(
    catalog: Path = typer.Option(..., "--catalog", help="A math-trace equations.json snapshot."),
    narrative: Path = typer.Option(..., "--narrative", help="The narrative JSON for the same topic."),
    formula: str = typer.Option(
        ..., "--formula", help="The formula's key in the catalog, for example michaelis_menten."
    ),
    record_id: str = typer.Option(..., "--id", help="The record's slug, for example michaelis-menten."),
    source_file: str = typer.Option(
        ...,
        "--source-file",
        help="The template's model.py path in math-trace, for example templates/biochemistry/src/model.py.",
    ),
    paper_store: Path = typer.Option(
        ..., "--paper-store", help="The paper-store root, for example /home/mark/paper-store."
    ),
    literature_id: str = typer.Option(
        ..., "--literature-id", help="The arXiv id of the paper the formula is taken from."
    ),
    literature_version: str = typer.Option(..., "--literature-version", help="The paper's version, for example v1."),
    locator: str = typer.Option(..., "--locator", help="Where the formula sits in the paper, for example 'page 4'."),
    out: Path = typer.Option(..., "--out", help="Where to write the formula record, as JSON."),
) -> None:
    """Assemble a formula record that cites a paper, and check the licence and version against the paper store."""
    literature = {"paper_store_id": literature_id, "version": literature_version, "locator": locator}
    _assemble_to_file(catalog, narrative, formula, record_id, source_file, paper_store, literature, out)


if __name__ == "__main__":
    app()
