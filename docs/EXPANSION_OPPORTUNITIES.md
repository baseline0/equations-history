# Expansion Opportunities: Next Equation Topics

This document catalogs high-value topics to add to equations-history, with curated references.

## Information Theory (Cover & Thomas)

**_Elements of Information Theory_** (2nd ed, 2006) is the canonical reference for foundational concepts in information theory, statistics, and machine learning. The equations bridge classical information theory → modern ML.

### Online Resources

| Resource | URL | Best For |
|----------|-----|----------|
| **NYU Summary (Backus)** | https://pages.stern.nyu.edu/~dbackus/BCZ/entropy/CoverThomas_summary.pdf | Quick lookup; Chapters 2-5, 7-9 with key definitions |
| **Cambridge Notes** | https://www.cl.cam.ac.uk/teaching/1819/InfoTheory/InfoTheoryNotes2019.pdf | Deep dives; 16 chapters (foundations to wavelets) |
| **Solution Manual** | https://eclass.icsd.aegean.gr/modules/document/file.php/ICSD549/Βιβλιογραφία/solutions%20of%20BOOK_Thomas&Cover.pdf | Worked examples; how equations apply in practice |
| **CMU Lecture Notes** | https://www.stat.cmu.edu/~cshalizi/350/2008/lectures/06a/lecture-06a.pdf | Gaussian-specific derivations |

### Recommended Topics to Add

#### Phase 5a: Entropy & Information (Chapter 2)
**Why:** Foundation for VAE KL divergence and mutual information bounds.

- [ ] **Entropy** — H(X) = -∑ p(x) log p(x)
- [ ] **Conditional Entropy** — H(X|Y)
- [ ] **Joint Entropy** — H(X,Y)
- [ ] **Mutual Information** — I(X;Y) = H(X) - H(X|Y)
- [ ] **Relative Entropy (KL Divergence)** — D(P||Q) = ∑ P(x) log(P(x)/Q(x))
- [ ] **Jensen's Inequality** — For concave functions (foundation for many bounds)

**Cross-links to ML:**
- KL divergence in VAE ELBO (already covered)
- Mutual information in information bottleneck theory
- Entropy in decision trees and information gain

#### Phase 5b: Data Compression & Source Coding (Chapter 5)
**Why:** Connects to autoencoder compression pipeline and rate-distortion theory.

- [ ] **Kraft Inequality** — Necessary condition for prefix codes
- [ ] **Huffman Code Length** — Average codeword length
- [ ] **Arithmetic Coding** — Near-optimal compression
- [ ] **Rate-Distortion Theorem** — D(R): minimum distortion at rate R
- [ ] **Blahut-Arimoto Algorithm** — Iterative computation of rate-distortion

**Cross-links to ML:**
- Autoencoders as lossy compression
- VAE trade-off between reconstruction loss and KL (rate-distortion analog)
- Bits-back coding (connection to VAE posteriors)

#### Phase 5c: Channel Coding & Capacity (Chapters 7-9)
**Why:** Foundation for understanding generalization, redundancy, and noise resilience.

- [ ] **Channel Capacity** — C = max I(X;Y)
- [ ] **Gaussian Channel Capacity** — C = (1/2) log₂(1 + S/N) bits
- [ ] **Shannon-Hartley Theorem** — Relates bandwidth, power, noise
- [ ] **Error Exponent** — How fast error probability decays
- [ ] **Fano's Inequality** — Lower bound on error probability

**Cross-links to ML:**
- Information bottleneck principle (neural network compression)
- Generalization bounds in statistical learning theory
- Noise robustness in deep learning

#### Phase 5d: Advanced Topics (Chapters 11-16)
**Why:** Connects to modern deep learning theory.

- [ ] **Maximum Entropy Principle** — p*(x) ∝ exp(-λH(x))
- [ ] **Kolmogorov Complexity** — K(x): shortest description of x
- [ ] **Algorithmic Mutual Information** — I_K(x;y)

**Cross-links to ML:**
- Implicit regularization in deep learning
- Complexity theory bounds on generalization

---

## Machine Learning & Statistics

### Recommended Topics (Beyond Current BERT/Autoencoders)

#### Optimizers
- [ ] **Stochastic Gradient Descent** — θ_{t+1} = θ_t - η·∇L(θ_t)
- [ ] **Momentum** — Accumulate gradient direction
- [ ] **Adam** — Adaptive learning rates per parameter
- [ ] **RMSprop** — Root mean square propagation

#### Regularization
- [ ] **L1/L2 Regularization** — λ ||θ||_p
- [ ] **Dropout** — Random neuron suppression during training
- [ ] **Batch Normalization** — Normalize layer activations
- [ ] **Layer Normalization** — Per-example normalization

#### Loss Functions
- [ ] **Cross-Entropy Loss** — Classification fundamental
- [ ] **Focal Loss** — Hard example weighting for imbalanced data
- [ ] **Contrastive Loss** — SimCLR, triplet loss, metric learning
- [ ] **Wasserstein Distance** — Optimal transport divergence

#### Generative Models
- [ ] **Diffusion Models** — Forward + reverse diffusion process
- [ ] **Score Matching** — Denoising score functions
- [ ] **GAN Generator & Discriminator Loss**
- [ ] **Flow-based Models** — Change of variables formula

#### Modern Architecture Components
- [ ] **Attention Bias** — Relative position embeddings (ALiBi, rotary embeddings)
- [ ] **Gated Linear Unit (GLU)** — σ(Wxg) ⊙ (Wxf)
- [ ] **Query-Key-Value Projections** — Modern attention variants
- [ ] **RoPE (Rotary Position Embeddings)** — Efficient position encoding

---

## How to Add a New Topic

Follow the Phase 1 pattern:

```python
# 1. Create src/equations_history/equations/topic.py
from equations_history.core import Equation

class TopicEquations:
    @staticmethod
    def equation_name() -> Equation:
        return Equation(
            name="Equation Name",
            latex=r"...",
            description="...",
            history="Why was this discovered? How did it evolve?",
            citations=["Author (Year). Title. Journal."],
            source_line=42,  # Line in this file
            concepts=["tag1", "tag2"]
        )

# 2. Add to CLI (src/equations_history/cli.py)
# 3. Add to taxonomy (src/equations_history/shared_taxonomy/examples.py)
# 4. Add tests (tests/test_equations/test_topic.py)
# 5. Run: just test && just serve
```

---

## Priority Ranking

### High Value (Directly used in modern ML)
1. **Entropy & Information Theory** (foundation for everything)
2. **Optimizers** (Adam, RMSprop)
3. **Attention Variants** (modern architectures depend on these)
4. **Diffusion Models** (generative modeling frontier)

### Medium Value (Important for understanding)
5. **Channel Capacity** (theoretical bounds)
6. **Regularization** (dropout, batch norm)
7. **Loss Functions** (contrastive, Wasserstein)

### Lower Priority (Specialized)
8. **Kolmogorov Complexity** (theoretical foundations)
9. **Rate-Distortion** (compression theory)
10. **Flow-based Models** (niche applications)

---

## Current Status

- ✅ **Autoencoders** (7 equations)
- ✅ **BERT** (7 equations)
- ✅ **Mechanical ↔ RLC Equivalence** (Lean proofs)
- ⏳ **Next Phase:** Information Theory fundamentals

---

## References

1. **Cover, T. M., & Thomas, J. A.** (2006). _Elements of Information Theory_ (2nd ed.). Wiley.
2. **Kingma, D. P., & Welling, M.** (2013). Auto-encoding variational Bayes. arXiv:1312.6114.
3. **Devlin, J., et al.** (2018). BERT: Pre-training of deep bidirectional transformers. arXiv:1810.04805.
4. **David Backus (NYU Stern).** Cover & Thomas Summary. https://pages.stern.nyu.edu/~dbackus/BCZ/entropy/

---

**Last updated:** 2026-09-21
