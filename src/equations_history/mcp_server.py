"""MCP stdio server for equations-history: read-only views of the equation registry.

Read tools reply with the fleet read envelope (fleet-coordination, contracts/read-envelope/FORMAT.md):
list_topics, list_equations, get_equation, list_formula_records and get_formula_record. Nothing here
writes, and no tool reaches the network. Bad identifiers are envelope errors, not tracebacks.
"""

from __future__ import annotations

import json
import re
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import equations_history.equations  # noqa: F401  importing the package registers every topic
from equations_history import registry
from equations_history.constants import REPO_ROOT
from equations_history.formula_record import validate_record

FORMULA_RECORDS_DIR = REPO_ROOT / "formula-records"
RECORD_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

CONTRACT = "fleet.read-envelope"
VERSION = "1.0"
SOURCE = "equations-history"


def envelope(view: str, data: dict[str, Any] | None = None, error: str | None = None) -> dict[str, Any]:
    """The read envelope: data on success, error on failure."""
    reply: dict[str, Any] = {"contract": CONTRACT, "version": VERSION, "source": SOURCE, "view": view}
    if error is None:
        reply["data"] = data
    else:
        reply["error"] = error
    return reply


def list_topics() -> dict[str, Any]:
    """The topics that have equations, such as autoencoders or diffusion."""
    return envelope("list_topics", {"topics": registry.topics()})


def list_equations(topic: str) -> dict[str, Any]:
    """The equations in one topic, with their short names and descriptions."""
    if topic not in registry.topics():
        return envelope("list_equations", error=f"unknown topic {topic!r}")
    equations = []
    for name in registry.names(topic):
        eq = registry.get(topic, name)
        equations.append({"name": name, "title": eq.name, "description": eq.description})
    return envelope("list_equations", {"topic": topic, "equations": equations})


def get_equation(topic: str, name: str) -> dict[str, Any]:
    """One equation in full: its LaTeX, its history, its citations and its concepts."""
    if topic not in registry.topics() or name not in registry.names(topic):
        return envelope("get_equation", error=f"unknown equation {topic}/{name}")
    eq = registry.get(topic, name)
    return envelope(
        "get_equation",
        {
            "topic": topic,
            "name": name,
            "title": eq.name,
            "latex": eq.latex,
            "description": eq.description,
            "history": eq.history,
            "citations": list(eq.citations),
            "concepts": list(eq.concepts),
        },
    )


def _record_ids() -> list[str]:
    """Stable slug ids of files that actually look like formula records (not sidecars)."""
    ids: list[str] = []
    if not FORMULA_RECORDS_DIR.is_dir():
        return ids
    for path in sorted(FORMULA_RECORDS_DIR.glob("*.json")):
        if not RECORD_ID_RE.match(path.stem):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and "core" in data:
            ids.append(path.stem)
    return ids


def list_formula_records() -> dict[str, Any]:
    """The ids of assembled formula records available for traceability checks."""
    return envelope("list_formula_records", {"records": _record_ids()})


def get_formula_record(record_id: str) -> dict[str, Any]:
    """One formula record with its full provenance and any schema violations, for offline traceability.

    The public website view strips file/source_line; this tool returns the stored record verbatim and
    reports validation errors so a caller can see when provenance is incomplete.
    """
    if not RECORD_ID_RE.match(record_id):
        return envelope("get_formula_record", error=f"invalid formula record id {record_id!r}")
    path = FORMULA_RECORDS_DIR / f"{record_id}.json"
    if not path.is_file():
        return envelope("get_formula_record", error=f"unknown formula record {record_id!r}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return envelope("get_formula_record", error=f"cannot read formula record {record_id!r}: {exc}")
    violations = validate_record(record)
    return envelope(
        "get_formula_record",
        {"record_id": record_id, "record": record, "validation_errors": violations},
    )


READ_TOOLS = (list_topics, list_equations, get_equation, list_formula_records, get_formula_record)


def build_server() -> MCPServer:
    """An MCP server with the three read-only tools, and nothing else."""
    server = MCPServer(
        "equations-history",
        instructions="Read-only views of the equation registry: topics, equations, and their citations.",
    )
    for fn in READ_TOOLS:
        server.add_tool(
            fn,
            name=fn.__name__,
            annotations=ToolAnnotations(
                read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
            ),
        )
    return server


def main() -> None:
    """Start the server on stdio. The MCP protocol owns stdout, so nothing else prints there."""
    build_server().run()


if __name__ == "__main__":
    main()
