# equations-history: AGMAI-Ready Contract

**Version**: 1.0 (Sep 22, 2026)  
**Status**: Contract for v0.9.0-rc1 release  
**Audience**: AGMAI, educators, students, mathematicians studying equation evolution

---

## What equations-history Is

**An interactive provenance demonstrator**: Shows how equations evolved across centuries, with code-grounded implementations, historical citations, and formal equivalence proofs.

**Not**: A complete historical encyclopedia, biographical dictionary, or primary-source archive.

**Role**: Bridge between human mathematical understanding and executable symbolic representations.

---

## Core Principle: Historical Provenance ≠ Mathematical Proof

An equation record may include:
- Historical narrative ("Newton's F=ma became dominant after 1700")
- Symbolic equivalence ("F=ma is algebraically equivalent to Lagrangian formulation")
- Formal proof ("Lean: mechanical and RLC systems are structurally equivalent under specified assumptions")

**These are distinct**. A historical claim is not validated by a mathematical proof, and vice versa.

---

## What equations-history Guarantees

### Guaranteed Features (v0.9.0+)

- ✅ **Code-grounded equations** — Every equation defined in SymPy; lives in `src/equations_history/equations/`
- ✅ **Source code links** — Every equation points to exact line in repository
- ✅ **Historical narrative** — Each topic includes cited story of how notation/interpretation changed
- ✅ **Interactive web UI** — Terminal-inspired interface for browsing, searching, visualizing
- ✅ **CLI access** — `equations-history learn <topic> --explain`
- ✅ **REST API** — JSON export of all equation metadata
- ✅ **LaTeX rendering** — MathJax renders equations in web UI
- ✅ **One-command start** — `just serve` launches web + API
- ✅ **Test coverage** — All equation metadata validated (90%+ test coverage)
- ✅ **Reproducibility** — Same environment → deterministic UI and API responses

### Experimental Features (Optional, May Change)

- 🔬 Lean formalization (optional per topic; proofs may remain incomplete)
- 🔬 Historical visualizations (timeline UI, not yet fully polished)
- 🔬 Interactive derivation steps (step-by-step walkthrough interface in development)

---

## What equations-history Does NOT Verify

**Explicitly out of scope**:

- ❌ Historical accuracy beyond cited sources — We link to papers, we don't archive the originals
- ❌ Complete historical narrative — We show selected milestones, not exhaustive surveys
- ❌ Biographical correctness — We discuss ideas, not biographical details
- ❌ Etymology or naming conventions — Why Lagrange was called "Lagrange," not our domain
- ❌ Pedagogical effectiveness — Whether a narrative helps learners (qualitative feedback only)
- ❌ Empirical validation of models — Models are shown, their real-world fit is user's responsibility

---

## What Qualifies as an "Evolution"

✅ **Counts as equation evolution**:

- Mathematical reformulation: "Force-based (F=ma) → Energy-based (Lagrangian L = T - V)" ← Same physics, different form
- Notation shift reflecting conceptual change: "i² = -1 was controversial; now accepted" ← Changed how we think about complex numbers
- Generalization: "Newton's second law → relativistic F = dp/dt" ← Extended domain
- Specialization: "Schrödinger equation with spherical symmetry → Solutions for hydrogen atom" ← Applied to specific case
- Computational form: "Theoretical conservation law → Discrete formulation for simulations" ← Same principle, different implementation
- Cross-domain unification: "Mechanical oscillator = RLC circuit (isomorphic systems)" ← Different domains, identical mathematics

❌ **Does NOT count**:

- Trivial algebraic rearrangement: "F=ma → ma=F" (just moving terms, no conceptual shift)
- Translation to different language: "Equation written in French vs. English" (no new insight)
- Typo fix: "Newton's original notation had an error, we use modern form" (correction, not evolution)
- Empirical update: "Newton's constant measured to better precision" (parameter refinement, not equation evolution)
- Notation preference: "Using bold **v** vs. arrow v̄ for vectors" (stylistic, no conceptual change)

---

## How Historical Claims Are Sourced

### Verified Sources ✅

- Peer-reviewed academic papers
- Books from university presses
- Primary sources (original papers when accessible)
- Historical archives (universities, libraries)

### Acceptable But Flagged 🟡

- Secondary historical accounts (with explicit caveat: "Reconstructed from secondary sources")
- Historical syntheses (e.g., "The Evolution of the Calculus" survey)
- Educational textbooks (cite the textbook, mark as "pedagogical interpretation")

### Not Acceptable ❌

- Memory / oral tradition without corroboration
- Wikipedia summaries without citation trail
- Loose paraphrasing of another's interpretation
- Conjecture about "probably how it happened"

**Rule**: If a historical claim cannot be linked to a checkable source, mark it as `historical_interpretation: unverified` and move it to a separate "Speculation" section.

---

## Formal Proofs: What They Do and Don't Claim

### A Lean Proof in equations-history

Example: "Mechanical oscillator and RLC circuit are structurally equivalent."

**Lean formalizes**:
- The state-space equations are mathematically identical under a parameter mapping
- Energy functions have the same structure
- Power dissipation formulas match

**Lean does NOT formalize**:
- That mechanical oscillators actually exist or behave this way
- That RLC circuits function as the mathematics predicts
- That the historical narrative is correct (just the math)
- That this was the reasoning Newton or Faraday used
- That the model captures reality (e.g., ignores friction, temperature, nonlinearities)

**README Statement**:
> "Lean proofs establish mathematical equivalence under explicitly stated assumptions. They do not validate empirical adequacy, historical interpretation, parameter estimation, or real-world applicability. See assumptions section for caveats."

### Verification Vocabulary for equations-history

| Status | Meaning | Example |
|--------|---------|---------|
| `source_cited` | Equation appears in cited work | "Kermack-McKendrick 1927, equation (1)" |
| `transcription_verified` | Equation faithfully transcribed from cited source | "Manual check: matches original notation exactly" |
| `symbolic_equivalent` | Modern form is algebraically equivalent to original | "Proven: F=ma ⟺ d(mv)/dt = F under constant m" |
| `formally_verified` | Lean theorem proven under stated assumptions | "Lean: MechanicalOscillator.energyEquals(RLCCircuit.energy)" |
| `historical_interpretation` | Human-curated claim about significance or adoption | "This formulation became standard post-1970" |
| `visual_verified` | Interactive visualization matches mathematical claim | "Latent space plot confirms VAE KL divergence decay" |

---

## Supported Interactions

### Terminal CLI (v0.9.0)

```bash
equations-history learn autoencoder --explain
# Outputs narrative + equations for autoencoder topic

equations-history list
# Shows all available topics

equations-history export bert --format json
# Exports BERT equations as JSON
```

### Web UI (v0.9.0)

- Browse topics via tabs or arrow keys
- View equation + narrative + citations
- Click "Jump to source" → GitHub line
- Interactive visualizations (latent space heatmap, attention matrix)
- Responsive mobile + desktop

### REST API (v0.9.0)

```bash
GET /api/equations/autoencoder
# Returns all equations for topic

GET /api/equations/autoencoder/elbo
# Returns specific equation with full metadata

GET /api/topics
# Lists all available topics
```

### Static Export

- `make export-static` → Generates static HTML for offline use or archival

---

## What's Included (v0.9.0)

### Core Topics (Complete)

| Topic | Equations | Scenarios | Lean Proofs | Visual |
|-------|-----------|-----------|------------|--------|
| Autoencoders | 7 (encoder, decoder, MSE, BCE, VAE ELBO, KL, reparameterization) | 2D latent space explorer | None (optional) | Heatmap |
| BERT | 7 (attention, multi-head, positional encoding, MLM, NSP, loss, fine-tuning) | Token classification | None (optional) | Attention matrix |
| Mechanical ↔ RLC | 8 (oscillator + RLC equivalence) | Force/current simulation | Complete (3 theorems) | Phase portrait |

### Available via CLI + API Only (No UI Yet)

- Optimization equations (Adam, SGD)
- Loss functions (cross-entropy, KL divergence)

---

## Scope Boundaries

### What We Cover

- ✅ Mathematical formulations and their evolutions
- ✅ Key historical milestones (selection, not exhaustive)
- ✅ Alternative notations and how they differ
- ✅ Cross-domain analogies (mechanical ↔ electrical)
- ✅ Symbolic equivalences with proof
- ✅ Modern executable implementations

### What We Explicitly Do NOT Cover

- 🚫 Complete biography of mathematicians
- 🚫 Social history of scientific acceptance
- 🚫 Detailed archival research (link to historians' work instead)
- 🚫 Comprehensive coverage of all historical variants (select key ones)
- 🚫 Empirical validation (that's for scientists using the equations)
- 🚫 Pedagogical assessment (we provide structure; teachers customize)

---

## Metadata Schema

Every equation record:

```python
@dataclass
class EquationRecord:
    topic: str                      # "Autoencoders", "BERT", etc.
    name: str                       # "VAE ELBO", "Attention mechanism"
    latex: str                      # SymPy-generated
    description: str                # What this equation represents
    
    source: Source
        # Cited historical source
        authors: List[str]
        year: int
        title: str
        doi: Optional[str]
        url: Optional[str]           # Link to paper if available
    
    historical_narrative: str        # How this equation fits the story
    
    assumptions: List[str]          # When is this equation valid?
    
    equivalent_forms: List[str]     # Alternative notations
    
    transformations: List[str]      # How this evolved from predecessors
    
    verification: Dict[str, VerificationRecord]
        source_cited: bool
        transcription_verified: bool
        symbolic_equivalent: bool
        formally_verified: Optional[str]  # Lean theorem name if proven
        historical_interpretation: str     # Claim + confidence level
    
    related_equations: List[str]    # Cross-references
    
    code_link: str                  # src/equations_history/equations/topic.py:line_number
```

---

## Release Versioning

### v0.9.0-rc1 (Release Candidate)

- ✅ 3 core topics complete (Autoencoders, BERT, Mechanical ↔ RLC)
- ✅ Web UI functional (terminal-inspired navigation)
- ✅ REST API functional (all endpoints working)
- ✅ Lean formalization for Mechanical ↔ RLC (proofs complete)
- ✅ All metadata fields populated
- ✅ Tests passing (90%+ coverage on metadata validation)
- ✅ CITATION.cff and README complete
- ⚠️ UI may iterate based on feedback (not frozen)

### v0.9.0 (Release)

- Same as rc1, with feedback incorporated

### v1.0.0 (When Ready)

- ✅ All from v0.9.0
- ✅ 5+ topics with historical narratives
- ✅ Lean proofs on 3+ topics
- ✅ Zenodo DOI minted
- ✅ UI refinements based on user feedback

---

## Known Limitations (Honest)

1. **Historical completeness** — We show selected milestones, not exhaustive timelines; true historians will note gaps
2. **Source availability** — Some primary sources are inaccessible; we link to secondary accounts with caveats
3. **Formalization coverage** — Lean proofs cover mathematical equivalence only, not historical claims
4. **Notation standardization** — Historical sources used wildly different notations; we normalize to modern SymPy
5. **Interpretation risk** — Our narrative selections reflect our understanding; other historians might emphasize different developments
6. **Limited topics** — v0.9.0 covers only autoencoders, BERT, and mechanics; expansion ongoing
7. **No timeline UI yet** — Historical visualizations are minimal; full timeline browser deferred to v1.0

---

## Integration with math-trace

equations-history and math-trace serve complementary roles:

**equations-history**: "Here's how F=ma evolved through Lagrangian, Hamiltonian, relativistic forms. See the narrative."

**math-trace**: "Here's the modern computational form of F=ma, its assumptions, test coverage, and formal verification."

**Together**: Researchers see historical context (equations-history) + production-ready implementation (math-trace).

---

## Approval & Sign-Off

**Contract finalized**: Sep 22, 2026  
**Author**: Mark Alexiuk  
**Reviewers**: (External review pending v0.9.0-rc1)

**Next checkpoint**: Week 1 (Sep 22–29) — Contract freeze complete, Epidemiology golden path starts (math-trace Week 2–3)

---

**For AGMAI**: This contract defines what equations-history is: a provenance demonstrator, not a proof system. It shows historical evolution + symbolic equivalences + selected formal proofs. The three status categories (source_cited, symbolic_equivalent, formally_verified, historical_interpretation) keep distinct claims distinct.
