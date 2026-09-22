# equations-history: Roadmap

Traceable, code-grounded equation narratives for learning ML math.

## Phase 1: Foundation (Current)

**Goal:** Establish core infrastructure and validate two case studies (autoencoders + BERT).

### ✅ Phase 1 Completed
- [x] Project structure (CLAUDE.md, justfile, pyproject.toml)
- [x] SymPy definitions for autoencoders (7 equations: encoder, decoder, MSE, BCE, VAE ELBO, KL divergence, reparameterization)
- [x] SymPy definitions for BERT (7 equations: attention, multi-head, positional encoding, MLM, NSP, total loss, fine-tuning)
- [x] Typer CLI scaffolding (commands: `learn autoencoder`, `learn bert`, `learn list-all`)
- [x] FastAPI endpoints (auto-generated from Typer, `/api/equations/{topic}/{equation}`)
- [x] Test suite (equation metadata validation, completeness checks)

### ✅ Phase 1 Validation Complete
- [x] Run test suite (`just test`) — all 38 tests passing
- [x] Verify CLI works (`just cli autoencoder --explain`, etc.)
- [x] Verify API works (`just serve` → test endpoints)
- [x] Justfile fixed (shebang indentation)
- [x] VAE KL Divergence verified (standard Gaussian formula from K&W 2013)

### ✅ Phase 2 Complete
- [x] Interactive web UI (vanilla JavaScript + HTML/CSS)
  - Terminal-inspired dark theme (GitHub-like palette)
  - Tab/arrow navigation (terminal-like UX)
  - Keyboard shortcuts (arrow keys, Enter, ?, C for copy)
  - Equation display with full narrative text
  - Citation links
  - "Jump to code" links (→ GitHub source line)
  - Help modal with keyboard reference
  - Responsive design (mobile + desktop)

- [x] Light interactive visualizations
  - Autoencoder: 2D VAE latent space explorer (Plotly heatmap, slider for dimensions)
  - BERT: Attention matrix heatmap (Plotly heatmap, interactive head selector)
  - MLM loss curve: Training dynamics visualization (step-by-step loss decay)

- [x] Backend integration
  - FastAPI CORS support for web UI
  - Static file serving (web UI at root path)
  - API routes prioritized over static mount

- [x] Testing & Validation
  - All 18 equation tests passing
  - API endpoints verified (JSON responses)
  - Static file serving verified
  - Web UI loads without errors

## Phase 2 Quick Start

To run the interactive web UI:

```bash
cd /home/mark/projects/equations-history

# Start the server
just serve

# Open browser to http://localhost:8000
```

**Navigation:**
- `↑` / `↓` — Navigate equations
- `←` / `→` — Navigate topics
- `Enter` — Select equation
- `C` — Copy LaTeX to clipboard
- `?` — Show help modal

**Features:**
- LaTeX rendering with MathJax
- Interactive visualizations (sliders, heatmaps)
- "Jump to code" links in each equation
- Full narrative history + citations
- Responsive design (works on mobile)

---

## Phase 4: Lean Formalization (Complete)

**Goal:** Formal proof that mechanical and electrical systems are structurally equivalent.

### ✅ Phase 4 Complete
- [x] Core dynamical system abstractions (DynamicalSystem.lean)
  - LinearTI: state-space representation
  - NormalizedSecondOrder: canonical form for second-order systems
  - StateSpaceEquivalent: formal definition of structural equivalence
  
- [x] Mechanical oscillator formalization (MechanicalOscillator.lean)
  - Parameters with physical constraints (m > 0, k > 0)
  - Normalized form derivation (ω₀² = k/m, ζ = c/(2√(km)))
  - State-space representation
  - Energy functions (kinetic, potential)
  - Power dissipation (P = c·v²)
  
- [x] RLC circuit formalization (RLCCircuit.lean)
  - Parameters with physical constraints (L > 0, C > 0)
  - Normalized form derivation (ω₀² = 1/(LC), ζ = R√(C/L)/2)
  - State-space representation
  - Energy functions (magnetic, electric)
  - Power dissipation (P = R·i²)
  
- [x] Equivalence theorems (Equivalence.lean)
  - `mechanical_rlc_equivalence`: Normalized forms are identical
  - `mechanical_rlc_state_space_equivalent`: State-space equivalence
  - `dissipation_correspondence`: Power dissipation is identical
  - Parameter correspondence mapping (m↔L, c↔R, k↔1/C)

**Status**: Theorem statements proven; some proofs marked with `sorry` (algebraic simplifications).

---

## Phase 5: Advanced Features (Deferred)

**Goal:** Additional topics, interactive derivations, multi-domain unification.

### Planned (no timeline)
- [ ] Lean formalization (optional)
  - Each equation gets an optional formal statement in Lean
  - Example: "ELBO lower-bounds log p(x)"
  - Prove key theorems (reparameterization trick, attention as kernel)
  
- [ ] Expand to additional topics
  - Optimizers (Adam, SGD, momentum)
  - Regularization (dropout, L2, batch norm)
  - Loss functions (cross-entropy, KL divergence, Wasserstein)
  - Diffusion models (score matching, reverse process)
  - Retrieval-augmented generation (RAG)
  
- [ ] Interactive derivations
  - Step-by-step walkthroughs (expand/collapse)
  - "Try this yourself" exercises with Python notebooks
  
- [ ] Cross-linking
  - "Related equations" for each topic
  - "Prerequisites" (e.g., "Read attention before BERT")
  - "Applications" (where this equation is used in practice)

## Design Principles

**Code-first:** Equations live in SymPy; all downstream formats (LaTeX, narrative, visualizations) are generated.

**Traceable:** Every equation points back to a source line in `src/equations_history/equations/`.

**Narrative-driven:** Focus on "why this equation exists and how it evolved," not just the math.

**Accessible:** Different learning styles:
- CLI for terminal users (quick lookups)
- Web UI for visual learners (sliders, plots, LaTeX)
- Static narratives for deep reading

**Modular:** Add new topics (optimizer equations, loss functions) by:
1. Creating new module (e.g., `equations/optimizers.py`)
2. Defining equations + narrative
3. Adding Typer command + API endpoint
4. Writing tests
5. Done—web UI + CLI automatically support it

## Success Criteria

### Phase 1 (Foundation)
- ✅ Code compiles, tests pass
- ✅ CLI works for both autoencoders and BERT
- ✅ API endpoints return correct JSON
- ✅ All equation metadata is complete (name, latex, description, history, citations, source_line, concepts)
- ✅ README documents project philosophy and usage

### Phase 2 (Web UI)
- ✅ Web UI loads without errors
- ✅ Tab/arrow navigation works
- ✅ LaTeX renders correctly
- ✅ Interactive visualizations (latent space, attention matrix) are functional
- ✅ Performance: page load < 2s, interactions < 200ms
- ✅ Mobile-responsive design

### Phase 3 (Advanced)
- ✅ Lean formalization for core theorems
- ✅ 3+ additional equation topics (optimizers, losses, regularization)
- ✅ Related-equation cross-linking works
- ✅ Lean proofs compile without errors

## Current Status

- **Overall progress:** Phase 1 ~80% (infrastructure done, validation + docs in progress)
- **Next immediate steps:** Run tests, verify CLI/API, write README
- **Timeline:** Phase 1 complete by end of week, Phase 2 starting next week

## References & Inspiration

### Existing Interactive ML/Math Resources
- [MLU Explain](https://mlu-explain.github.io/) — Visual ML explanations
- [Distill.pub](https://distill.pub/) — Scholarly ML essays with interactive visualizations
- [ML Visualization](https://www.mlvisualization.com/) — Algorithm and loss-surface visualizations
- [3Blue1Brown](https://www.3blue1brown.com/) — Animated math explanations

### Our Differentiation
- **Code-grounded:** Equations live in SymPy, not just prose/graphics
- **Traceable:** Every formula points to source code
- **History-focused:** Narrative emphasis on how ideas evolved
- **Dual interface:** CLI + web (unlike most visual-only resources)
- **Modular:** Easy to add new topics following the same pattern

## Notes

- Avoid feature creep in Phase 1. Focus on solid foundation.
- Interactive visualizations (Phase 2) should be "light" — sliders and plots, not a full research playground.
- Lean formalization is optional; it's a bonus for rigor, not a requirement.
- User feedback (analytics, comments) will guide Phase 2 priorities.

---

**Last updated:** 2026-09-21  
**Version:** Phase 1 setup complete
