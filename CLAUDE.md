# equations-history: Traceable Equation Narratives

Code-first, interactive learning for ML mathematics. Each formula is tied to source code, narrative context, and (optionally) formal proof.

**For universal rules, see `~/.claude/CLAUDE.md`.**

## Quick Start

```bash
uv sync                           # Install dependencies
just test                         # Run test suite
just serve                        # Start web server (localhost:8000)
uv run learn autoencoder --help   # CLI help
```

## Project Philosophy

**Code is source of truth.** Equations live in SymPy first, then render into narrative, web UI, and (optionally) Lean formalizations. This preserves traceability: every formula points back to a specific line in `src/`.

Similar to math-trace, but optimized for **learning + interactivity** rather than publication. Sibling project with shared DNA.

## Phase 1 Scope

Two case studies:
- **Autoencoders** (standard + VAE, including reparameterization trick)
- **BERT** (scaled dot-product attention + MLM loss)

Deliverables:
- ✅ SymPy definitions (source of truth)
- ✅ Typer CLI (`learn autoencoder --explain`, etc.)
- ✅ FastAPI endpoints (auto-generated from typer)
- ✅ Static narrative (equation + history + citations)
- ⏳ Web UI (Phase 2)
- ⏳ Interactive visualizations (Phase 2)
- ⏳ Lean formalization (Phase 2, optional)

## Project Structure

```
equations-history/
├── pyproject.toml                 # Dependencies, tool config
├── .python-version                # "3.13"
├── justfile                       # Tasks
├── README.md                      # Public overview
├── TODO.md                        # Phase 1-3 roadmap
├── CLAUDE.md                      # This file
│
├── src/equations_history/
│   ├── __init__.py
│   ├── cli.py                     # Typer CLI entry point
│   ├── api.py                     # FastAPI endpoints (auto-generated from CLI)
│   └── equations/
│       ├── __init__.py
│       ├── autoencoders.py        # Autoencoder SymPy definitions + narrative
│       └── bert.py                # BERT SymPy definitions + narrative
│
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   └── test_equations/
│       ├── test_autoencoders.py   # Verify SymPy + narrative export
│       └── test_bert.py           # Verify BERT equations
│
└── docs/
    ├── ARCHITECTURE.md            # System design (if needed)
    └── narrative/                 # Static narratives for each equation
        ├── autoencoder.md
        └── bert.md
```

## Core Patterns

### Equations in SymPy

Each equation module exports:
- **Symbols & definitions** (e.g., `encoder`, `decoder`, `reconstruction_loss`)
- **Narrative metadata** (history, citations, key insights)
- **Traceability** (source line, related concepts)

Example (src/equations_history/equations/autoencoders.py):
```python
import sympy as sp

# Symbols
x = sp.Symbol('x', real=True)  # Input
z = sp.Symbol('z', real=True)  # Latent code
# ... etc

class AutoencoderEquations:
    """Deterministic autoencoder definitions."""
    
    @staticmethod
    def encoder():
        """Encoder: z = f_φ(x).
        
        Source: model.py:42
        History: From early work on autoencoders (Hinton, Salakhutdinov 2006)
        """
        # Return SymPy expression
        pass
    
    # ... more methods
```

### CLI Command Structure

Typer commands mirror the equation structure:
```bash
learn autoencoder              # List all autoencoder concepts
learn autoencoder --explain    # Show all equations + narrative
learn autoencoder encoder      # Show just encoder equation
learn bert attention           # Show BERT attention mechanism
```

### FastAPI Auto-Generation

From typer commands, auto-generate FastAPI endpoints:
```
GET /api/equations/autoencoder/encoder
GET /api/equations/bert/attention
```

Response includes: equation LaTeX, narrative, citations, source line.

## Commands

```bash
just test              # Run pytest
just fmt               # Format + lint (ruff)
just check             # Type check + lint
just serve             # Start FastAPI dev server
just cli               # Run Typer CLI help
```

## Coding Standards

**Python:**
- Type hints on all functions (PEP 484)
- Docstrings explaining equation meaning, not just code (Google style)
- Tests verify SymPy exports + narrative metadata

**SymPy:**
- Clear symbol definitions (annotate with units/domains if relevant)
- Narrative docstrings tie each equation to history/usage
- Cite references (papers, blog posts, etc.)

**Narrative:**
- Focus on "why this equation exists" and "how it evolved"
- Link equations to practical use cases (autoencoders in image compression, BERT in NLP)
- Use citations from sources provided by user

## Git Workflow

```bash
git status                        # Check current state
git add path/to/file              # Stage specific files
just commit                       # Commit with auto-generated message
```

Commit messages should reference:
- Which equation(s) were added/updated
- If narrative or SymPy definitions changed
- Related ADR or design decision (if applicable)

Example:
```
feat: Add standard autoencoder equations (encoder, decoder, MSE loss)

Defines core autoencoder SymPy expressions with narrative context
linking to Hinton & Salakhutdinov (2006). Includes both deterministic
and VAE variants.

Related: Phase 1 scope (autoencoders + BERT case studies)
```

## Testing & Verification

```bash
just test                         # Full test suite
uv run pytest tests/test_equations/ -v  # Just equation tests
uv run mypy src/                  # Type check
```

Tests verify:
- SymPy expressions are valid (no syntax errors)
- Narrative metadata is complete (citations, history)
- CLI commands map correctly to equation definitions
- API responses serialize correctly (JSON-safe)

## Extending Phase 1

To add a new equation module:

1. Create `src/equations_history/equations/my_topic.py`
2. Define `MyTopicEquations` class with SymPy + narrative
3. Add Typer command in `cli.py`: `@app.command()`
4. Write test in `tests/test_equations/test_my_topic.py`
5. Run `just test` to verify

## References

- **SymPy Docs**: https://docs.sympy.org/
- **Typer Docs**: https://typer.tiangolo.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **math-trace**: Sibling project (derivation → publication)
- **Comparison to existing tools**: See TODO.md (positioning section)

## Questions?

See README.md for high-level overview or check tests/ for usage examples.
