# equations-history Roadmap

Status: active development. This file tracks current state and near-term direction; detailed topic backlog lives in [`docs/EXPANSION_OPPORTUNITIES.md`](docs/EXPANSION_OPPORTUNITIES.md).

## Current (observed on `main`)

- **Equation modules (SymPy + narrative metadata):** `autoencoders`, `bert`, `biochemistry`, `diffusion`, `entropy`, `loss_functions`, `optimizers`, `quantum`, `regularization`.
- **Interfaces:** Typer CLI (`learn`), FastAPI endpoints, HTTP server, MCP server (`serve-mcp`), formula record/catalog/pages tooling.
- **Docs/artifacts:** `README.md`, `CLAUDE.md`, `docs/EXPANSION_OPPORTUNITIES.md`, narrative walkthroughs under `docs/narrative/`, lean/crawl/formula-record support files.
- **Quality gates:** `just test`, `just check`, `just fmt`, `just test-unit`; pre-commit hooks configured.

## Near-term

- **Doc/structure alignment:** Keep README/CLAUDE structure and phase claims aligned with actual modules, interfaces, and tests.
- **Web UI / interactive learning (Phase 2):** Lightweight browser UI for equation browsing, narrative context, and small visualizations; keep CLI/API/MCP contracts stable.
- **Topic expansion:** Prioritize backlog in `docs/EXPANSION_OPPORTUNITIES.md`; add each topic with SymPy definition, narrative/citations, CLI/API exposure, and tests.
- **Formula records/pages:** Continue hardening catalog/record bundle/page workflows and review gating (`pages-build`, `pages-approve*`, `publish-check`).
- **Provenance & interoperability:** Maintain traceability from equation to source/citations and compatibility with downstream consumers (e.g. math-trace/tool-rag workflows where applicable).

## Deferred / evaluate

- **Lean formalization:** Optional; only where it adds verifiable value without obscuring the learning narrative.
- **Interactive derivation exercises:** After core UI and topic coverage stabilize.
- **Release/versioning criteria:** Define when the package/API/MCP surfaces are considered stable enough for a tagged release.
