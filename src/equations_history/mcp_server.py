"""MCP stdio server for equations-history: read-only views of the equation registry.

Three tools, each replying with the fleet read envelope (fleet-coordination, contracts/read-envelope/FORMAT.md):
list_topics, list_equations and get_equation. Nothing here writes, and no tool reaches the network. A bad topic or
equation name is an envelope with an error, not a traceback, so a caller can always parse the reply.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import equations_history.equations  # noqa: F401  importing the package registers every topic
from equations_history import registry

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


READ_TOOLS = (list_topics, list_equations, get_equation)


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
