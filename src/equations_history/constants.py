"""Repository root for the equations_history package."""

from pathlib import Path

# This repository's root: src/equations_history/constants.py -> repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CITATION_GRAPH_SCHEMA_PATH: Path = REPO_ROOT / "contracts" / "citation_graph.schema.json"

# The package's own data: the formula catalogs copied from math-trace, and the narratives written here.
PACKAGE_ROOT: Path = Path(__file__).resolve().parent
CATALOG_DIR: Path = PACKAGE_ROOT / "catalogs"
NARRATIVE_DIR: Path = PACKAGE_ROOT / "narratives"

FORMULA_RECORD_SCHEMA_PATH: Path = REPO_ROOT / "contracts" / "formula_record.schema.json"
