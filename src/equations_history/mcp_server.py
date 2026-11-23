"""MCP server for equations-history: read-only tools and addressable resources.

Read tools and resources reply with the fleet read envelope (fleet-coordination,
contracts/read-envelope/FORMAT.md). Nothing here writes, and no tool or resource reaches the network:
Stacks and paper references are pointer-only snapshots. Bad identifiers are envelope errors, not tracebacks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import equations_history.equations  # noqa: F401  importing the package registers every topic
from equations_history import registry
from equations_history.constants import CATALOG_DIR, REPO_ROOT
from equations_history.formula_catalog import CatalogError
from equations_history.formula_record import validate_record
from equations_history.record_bundle import build_bundle, read_reviews

FORMULA_RECORDS_DIR = REPO_ROOT / "formula-records"
FULL_RECORDS_DIR = REPO_ROOT / "formula-records-full"
RECORD_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CATALOG_NAME_RE = RECORD_ID_RE


def _record_path(record_id: str) -> tuple[Path, bool]:
    """Full provenance record when assembled, else the public website view."""
    full = FULL_RECORDS_DIR / f"{record_id}.json"
    if full.is_file():
        return full, True
    return FORMULA_RECORDS_DIR / f"{record_id}.json", False


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
    paths = set(FORMULA_RECORDS_DIR.glob("*.json")) | set(FULL_RECORDS_DIR.glob("*.json"))
    for path in sorted(paths):
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
    path, complete = _record_path(record_id)
    if not path.is_file():
        return envelope("get_formula_record", error=f"unknown formula record {record_id!r}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return envelope("get_formula_record", error=f"cannot read formula record {record_id!r}: {exc}")
    violations = validate_record(record)
    return envelope(
        "get_formula_record",
        {
            "record_id": record_id,
            "record": record,
            "provenance_complete": complete,
            "validation_errors": violations,
        },
    )


def get_record_bundle(record_id: str) -> dict[str, Any]:
    """One formula record joined with its crosswalk, verification, review pin and narrative chunk."""
    if not RECORD_ID_RE.match(record_id):
        return envelope("get_record_bundle", error=f"invalid formula record id {record_id!r}")
    try:
        bundle = build_bundle(record_id)
    except CatalogError as error:
        return envelope("get_record_bundle", error=str(error))
    return envelope("get_record_bundle", bundle)


def get_record_crosswalk(record_id: str) -> dict[str, Any]:
    """The stable ids that tie one record to math-trace, tool-lit-review and tool-rag."""
    if not RECORD_ID_RE.match(record_id):
        return envelope("get_record_crosswalk", error=f"invalid formula record id {record_id!r}")
    try:
        bundle = build_bundle(record_id)
    except CatalogError as error:
        return envelope("get_record_crosswalk", error=str(error))
    return envelope("get_record_crosswalk", {"record_id": record_id, **bundle["identity"]})


def get_narrative_chunk(record_id: str) -> dict[str, Any]:
    """A chunk-ready narrative with provenance, for tool-rag indexing without a PDF."""
    if not RECORD_ID_RE.match(record_id):
        return envelope("get_narrative_chunk", error=f"invalid formula record id {record_id!r}")
    try:
        bundle = build_bundle(record_id)
    except CatalogError as error:
        return envelope("get_narrative_chunk", error=str(error))
    return envelope(
        "get_narrative_chunk",
        {
            "record_id": record_id,
            "record_key": bundle["identity"]["rag_record_key"],
            "record_digest": bundle["record_sha256"],
            "text": bundle["narrative_text"],
        },
    )


def get_catalog_manifest(catalog: str) -> dict[str, Any]:
    """The snapshot pin for one math-trace catalog: source, source_commit and sha256."""
    if not CATALOG_NAME_RE.match(catalog):
        return envelope("get_catalog_manifest", error=f"invalid catalog name {catalog!r}")
    path = CATALOG_DIR / f"{catalog}.manifest.json"
    if not path.is_file():
        return envelope("get_catalog_manifest", error=f"unknown catalog {catalog!r}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return envelope("get_catalog_manifest", error=f"cannot read manifest for {catalog!r}: {error}")
    return envelope("get_catalog_manifest", {"catalog": catalog, "manifest": manifest})


READ_TOOLS = (
    list_topics,
    list_equations,
    get_equation,
    list_formula_records,
    get_formula_record,
    get_record_bundle,
    get_record_crosswalk,
    get_narrative_chunk,
    get_catalog_manifest,
)


def _json_resource(fn: Any, *args: Any) -> str:
    """Resource payloads are JSON strings of the same read envelope the tools return."""
    return json.dumps(fn(*args), ensure_ascii=False, indent=2)


def _resource_topics() -> str:
    return _json_resource(list_topics)


def _resource_index() -> str:
    return _json_resource(list_formula_records)


def _resource_reviews() -> str:
    return _json_resource(lambda: envelope("reviews", read_reviews()))


def _resource_equation(topic: str, name: str) -> str:
    return _json_resource(get_equation, topic, name)


def _resource_bundle(record_id: str) -> str:
    return _json_resource(get_record_bundle, record_id)


def _resource_crosswalk(record_id: str) -> str:
    return _json_resource(get_record_crosswalk, record_id)


def _resource_narrative(record_id: str) -> str:
    """Plain text for RAG; an error envelope is still JSON so failures stay machine-readable."""
    reply = get_narrative_chunk(record_id)
    if "error" in reply:
        return json.dumps(reply, ensure_ascii=False)
    return str(reply["data"]["text"])


def _resource_manifest(catalog: str) -> str:
    return _json_resource(get_catalog_manifest, catalog)


def build_server() -> MCPServer:
    """An MCP server with read-only tools and addressable resources, and nothing else."""
    server = MCPServer(
        "equations-history",
        instructions="Read-only equation registry, formula-record bundles and provenance snapshots. No network access.",
    )
    for fn in READ_TOOLS:
        server.add_tool(
            fn,
            name=fn.__name__,
            annotations=ToolAnnotations(
                read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
            ),
        )

    server.resource("equations://topics", mime_type="application/json")(_resource_topics)
    server.resource("equations://equation/{topic}/{name}", mime_type="application/json")(_resource_equation)
    server.resource("records://index", mime_type="application/json")(_resource_index)
    server.resource("records://reviews", mime_type="application/json")(_resource_reviews)
    server.resource("records://formula/{record_id}/bundle", mime_type="application/json")(_resource_bundle)
    server.resource("records://formula/{record_id}/crosswalk", mime_type="application/json")(_resource_crosswalk)
    server.resource("records://formula/{record_id}/narrative", mime_type="text/plain")(_resource_narrative)
    server.resource("records://manifest/{catalog}", mime_type="application/json")(_resource_manifest)
    return server


def main() -> None:
    """Start the server on stdio. The MCP protocol owns stdout, so nothing else prints there."""
    build_server().run()


if __name__ == "__main__":
    main()
