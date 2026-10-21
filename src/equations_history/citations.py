"""Citation graph ingest: tool-lit-review's papers/graph.json, validated against the contract, read for one paper at a time.

Design Intent:
- Reads only. The producer is tool-lit-review; the contract is contracts/citation_graph.schema.json. This module never
  imports tool-lit-review.
- An edge is (citing, cited), as the producer writes it. ``cites`` and ``cited_by`` are read from that order and nothing
  else is inferred.
- A file that fails the schema is refused, not repaired.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from equations_history.constants import CITATION_GRAPH_SCHEMA_PATH


class GraphError(ValueError):
    """The citation graph file does not match the contract."""


@dataclass(frozen=True)
class CitationGraph:
    nodes: frozenset[str]
    edges: tuple[tuple[str, str], ...]

    def cites(self, paper: str) -> tuple[str, ...]:
        """Papers in the graph that ``paper`` cites."""
        return tuple(sorted({cited for citing, cited in self.edges if citing == paper}))

    def cited_by(self, paper: str) -> tuple[str, ...]:
        """Papers in the graph that cite ``paper``."""
        return tuple(sorted({citing for citing, cited in self.edges if cited == paper}))


def load_graph(path: Path, schema_path: Path = CITATION_GRAPH_SCHEMA_PATH) -> CitationGraph:
    """Read and validate a citation graph file. Raises GraphError with the first contract violation."""
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        location = "/".join(str(part) for part in errors[0].path) or "(root)"
        raise GraphError(f"{path.name} does not match the contract at {location}: {errors[0].message}")
    nodes = frozenset(payload["nodes"])
    edges = tuple((citing, cited) for citing, cited in payload["edges"])
    unknown = sorted({paper for edge in edges for paper in edge} - nodes)
    if unknown:
        raise GraphError(f"edges name papers that are not nodes: {unknown[:5]}")
    return CitationGraph(nodes=nodes, edges=edges)
