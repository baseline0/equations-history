"""Repository root for the equations_history package."""

from pathlib import Path

# This repository's root: src/equations_history/constants.py -> repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CITATION_GRAPH_SCHEMA_PATH: Path = REPO_ROOT / "contracts" / "citation_graph.schema.json"
