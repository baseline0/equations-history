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

### 📋 Phase 1 In Progress
- [ ] Run test suite (`just test`) — verify all equations pass
- [ ] Verify CLI works (`just cli autoencoder --explain`, etc.)
- [ ] Verify API works (`just serve` → test endpoints)
- [ ] Initial commit + push to GitHub

### 📋 Phase 1 Pending
- [ ] Static narrative pages (Markdown/HTML) for each equation topic
  - Generate narrative HTML from equation metadata
  - Add "jump to code" links (→ source line in GitHub)
  - Add visualization placeholders for Phase 2
- [ ] Documentation (README.md with project overview)
- [ ] Minimal web UI shell (Phase 2 starting point)

## Phase 2: Interactive Visualizations

**Goal:** Add web UI with light interactive visualizations (sliders, latent space 2D plot, attention matrix heatmap).

### Planned (not yet started)
- [ ] Build web UI (React or vanilla JS)
  - Tab/arrow navigation (terminal-like UX)
  - Equation display with LaTeX rendering
  - Narrative text
  - Citation links
  - "Jump to code" links
  
- [ ] Light interactive visualizations
  - Autoencoder: 2D VAE latent space explorer (slider to change dimensions)
  - BERT: Attention matrix heatmap (interactive slider for layer/head)
  - Loss curves: simple plots showing how losses evolve during training
  
- [ ] Live code examples (Python/PyTorch snippets that users can run in browser via Pyodide)

- [ ] Performance monitoring
  - Log which equations are accessed most
  - Feedback form for learners

## Phase 3: Advanced Features (Deferred)

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
