# equations-history

**Traceable, code-grounded equation narratives for learning ML math.**

Think of this as a "history of equations" told through code, narrative, and (eventually) interactive visualizations. Each formula is tied to:
- **Source code** (SymPy, points to a specific line)
- **Narrative context** (why it exists, how it evolved)
- **Citations** (original papers)
- **Practical use** (where this equation appears in ML)

Available as:
- 📟 **CLI** (for quick lookups: `learn autoencoder --explain`)
- 🌐 **Web UI** (for visual learning with sliders and plots—Phase 2)
- 📚 **Static narratives** (for deep reading)

## Quick Start

```bash
# Install dependencies
uv sync

# List all equations
uv run learn list-all

# Explain autoencoders (with full narrative)
uv run learn autoencoder --explain

# Get a specific equation
uv run learn autoencoder encoder

# Show BERT attention mechanism
uv run learn bert scaled_dot_product_attention --citations

# Start the web server (Phase 2)
just serve
```

## What's Inside

### Phase 1: Autoencoders & BERT

**Autoencoders** (7 equations):
- Deterministic encoder/decoder
- MSE and binary cross-entropy reconstruction losses
- VAE ELBO (Evidence Lower Bound)
- KL divergence for Gaussians
- Reparameterization trick

**BERT** (7 equations):
- Scaled dot-product attention
- Multi-head attention
- Positional encoding
- Masked language modeling (MLM) loss
- Next sentence prediction (NSP) loss
- Total pretraining loss
- Fine-tuning strategy

Each equation includes:
- Mathematical notation (LaTeX)
- Plain-language description
- Historical context (who discovered it, when, why)
- Academic citations
- Key concepts and related topics

### Project Structure

```
equations-history/
├── src/equations_history/
│   ├── equations/
│   │   ├── autoencoders.py      # Autoencoder definitions
│   │   └── bert.py               # BERT definitions
│   ├── cli.py                    # Typer CLI entry point
│   └── api.py                    # FastAPI endpoints
├── tests/
│   └── test_equations/           # Equation validation tests
├── TODO.md                       # Phase 1-3 roadmap
└── CLAUDE.md                     # Project configuration
```

## Philosophy

**Code is source of truth.** Equations are defined in SymPy (Python), then rendered into:
- CLI output (terminal-friendly text)
- Web UI (LaTeX, interactive plots)
- Static narratives (Markdown/HTML)
- (Eventually) Lean formalizations (formal proofs)

This preserves **traceability**: every formula points back to a specific line in code. If you want to understand *why* an equation is written a certain way, you can see the SymPy definition and its metadata.

## Usage Patterns

### For Terminal Lovers
```bash
# Quick lookup
uv run learn autoencoder encoder

# Detailed explanation with citations
uv run learn bert attention --citations

# List all topics
uv run learn list-all
```

### For Visual Learners (Phase 2)
```bash
# Start the web server
just serve

# Visit http://localhost:8000
# - Navigate with tabs/arrows (terminal-like UX)
# - Click equations to expand
# - Interact with visualizations (sliders, plots)
# - Search across topics
```

## API Endpoints (FastAPI)

All CLI commands are also available as HTTP endpoints:

```bash
# List all autoencoder equations
curl http://localhost:8000/api/equations/autoencoder

# Get a specific equation
curl http://localhost:8000/api/equations/autoencoder/encoder

# Get all BERT equations
curl http://localhost:8000/api/equations/bert

# Get a specific BERT equation
curl http://localhost:8000/api/equations/bert/scaled_dot_product_attention
```

Response format:
```json
{
  "name": "Scaled Dot-Product Attention",
  "latex": "\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^\\top}{\\sqrt{d_k}}\\right)V",
  "description": "Core attention mechanism...",
  "history": "Introduced in 'Attention is All You Need' (Vaswani et al., 2017)...",
  "citations": ["Vaswani et al. (2017)..."],
  "source_line": 30,
  "concepts": ["attention", "self-attention", "transformer"]
}
```

## Development

```bash
# Run tests
just test

# Type check
just check

# Format code
just fmt

# View all available tasks
just --list
```

## Why This Project?

Existing interactive ML/math resources (MLU-Explain, Distill.pub, ML Visualized) are excellent at **visual explanations**. But they typically:
- Treat equations as illustrations (art, not code)
- Don't emphasize narrative/history
- Aren't designed for easy extension

This project differs by:
- **Making equations executable code** (SymPy, not just LaTeX)
- **Emphasizing history** ("how mathematicians discovered this")
- **Enabling easy extension** (add a new topic by writing a Python module)
- **Providing multiple interfaces** (CLI + web + static narratives)
- **Tracing back to source** (click an equation → see its SymPy definition)

It's a **learning tool for practitioners** who want to understand not just *what* equations do, but *why* they exist and *where* they came from.

## Roadmap

**Phase 1 (Current):** Foundation  
- ✅ SymPy definitions for autoencoders + BERT
- ✅ CLI + FastAPI endpoints
- ✅ Test suite
- 📋 Static narratives + README

**Phase 2:** Interactive web UI  
- Light visualizations (latent space explorer, attention heatmap)
- Terminal-like navigation (tabs/arrows)
- Mobile-responsive design

**Phase 3:** Advanced features (deferred)  
- Lean formalization (optional)
- More topics (optimizers, regularization, diffusion models)
- Interactive derivations with exercises

See [TODO.md](TODO.md) for detailed roadmap.

## Contributing

To add a new topic (e.g., optimizer equations):

1. Create `src/equations_history/equations/optimizers.py`
2. Define `OptimizerEquations` class with methods returning `Equation` dataclasses
3. Add Typer command in `cli.py`
4. Add FastAPI endpoint in `api.py`
5. Write tests in `tests/test_equations/test_optimizers.py`
6. Run `just test` to verify

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.

## References

- [Autoencoder survey (Goodfellow et al., 2016)](https://www.deeplearningbook.org/)
- [BERT paper (Devlin et al., 2018)](https://arxiv.org/abs/1810.04805)
- [Attention is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762)
- [SymPy documentation](https://docs.sympy.org/)
- [Typer CLI framework](https://typer.tiangolo.com/)

## License

MIT

---

**Questions?** See [CLAUDE.md](CLAUDE.md) for project details or check [TODO.md](TODO.md) for roadmap.
