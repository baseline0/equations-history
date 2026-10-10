# Walkthrough: Closed-form KL divergence for a Gaussian encoder

> **DRAFT for human review.** Not finished. Each algebra step was checked
> with SymPy 1.14 (see "Verification" at the end). Claims marked **[REVIEW]**
> need a human check before this leaves draft.

**Equation:** `KL(q_φ(z|x) || p(z))` with `q = N(μ, σ²)` and prior `p = N(0, 1)`, one latent dimension.
This is the regularization term of the VAE ELBO (see `vae_elbo` and `vae_kl_divergence_gaussian` in `src/equations_history/equations/autoencoders.py`).

**Target result** (matches `vae_kl_divergence_gaussian`, summed over `j` for a diagonal multi-dimensional latent):

$$
\mathrm{KL}\big(\mathcal{N}(\mu,\sigma^2)\,\|\,\mathcal{N}(0,1)\big) = \tfrac{1}{2}\left(\mu^2 + \sigma^2 - \log\sigma^2 - 1\right)
$$

---

## Steps

### Step 1: Definition

$$
\mathrm{KL}(q\|p) = \int q(z)\,\big[\log q(z) - \log p(z)\big]\,dz = \mathbb{E}_{q}\big[\log q(z) - \log p(z)\big]
$$

### Step 2: Write both log-densities

$$
\log q(z) = -\tfrac{1}{2}\log(2\pi\sigma^2) - \frac{(z-\mu)^2}{2\sigma^2}
$$

$$
\log p(z) = -\tfrac{1}{2}\log(2\pi) - \frac{z^2}{2}
$$

*Check:* substitute `μ=0, σ=1` into the first line; it reduces to the second. Verified (SymPy).

### Step 3: Subtract

$$
\log q(z) - \log p(z) = -\tfrac{1}{2}\log\sigma^2 - \frac{(z-\mu)^2}{2\sigma^2} + \frac{z^2}{2}
$$

The `log(2π)` terms cancel. The `-½log(2π)` in `log p` and the `-½log(2π)` in `log q` differ by `-½log(2π) + ½log(2π) = 0`.

### Step 4: Take expectations under q

Use the two Gaussian moments:

- `E_q[(z-μ)²] = σ²` (variance of `q`)
- `E_q[z²] = μ² + σ²` (because `E_q[z²] = Var(z) + (E_q z)² = σ² + μ²`)

Then

$$
\mathrm{KL} = -\tfrac{1}{2}\log\sigma^2 - \frac{\sigma^2}{2\sigma^2} + \frac{\mu^2 + \sigma^2}{2}
$$

Note `σ²/(2σ²) = ½`, so the middle term is `-½`.

### Step 5: Simplify

$$
\mathrm{KL} = \tfrac{1}{2}\left(\mu^2 + \sigma^2 - \log\sigma^2 - 1\right)
$$

This is the target result. **Verified:** SymPy integrates `q·(log q − log p)` over `ℝ` with `σ > 0` and the difference from the target simplifies to `0`.

### Step 6: Why the minimum is at `μ = 0, σ = 1` **[REVIEW]**

Set `f(μ, σ) = ½(μ² + σ² − log σ² − 1)`.

- `∂f/∂μ = μ`. This is zero only at `μ = 0`. **Verified.**
- `∂f/∂σ = σ − 1/σ`. This is zero only at `σ = 1` (for `σ > 0`). **Verified.**
- Non-negativity: with `x = σ²`, `x − 1 − log x ≥ 0` for `x > 0`, with equality at `x = 1`. Stated here as a standard inequality (`log x ≤ x − 1`); the reviewer should confirm they want it proven inline. The stationary point argument above shows it is the only critical point; the sign argument is what shows it is a minimum.

So `KL ≥ 0` and `KL = 0` exactly when `q = p`. **[REVIEW]** the "exactly when" uses the non-negativity inequality from the previous bullet.

### Step 7: Multi-dimensional latent **[REVIEW]**

With a diagonal covariance `diag(σ_1², …, σ_d²)` and prior `N(0, I)`, the joint KL factorizes over independent dimensions, so the terms add:

$$
\mathrm{KL} = \tfrac{1}{2}\sum_{j=1}^{d}\left(\mu_j^2 + \sigma_j^2 - \log\sigma_j^2 - 1\right)
$$

This matches the sum in `vae_kl_divergence_gaussian`. The factorization step is standard but not re-derived here.

---

## Exercises

1. Compute `KL` for `μ = 1, σ = 1`.
2. Compute `KL` for `μ = 0, σ = 2`.
3. For a 2-dimensional latent with `μ = (1, 0)` and `σ = (1, 1)`, compute the total KL.
4. Show that `∂f/∂σ = 0` has no solution other than `σ = 1` when `σ > 0`.

## Answers

1. `½(1 + 1 − log 1 − 1) = ½(1) = 0.5`.
2. `½(0 + 4 − log 4 − 1) = ½(3 − log 4) = ½(3 − 1.3863) ≈ 0.8069`.
3. Dimension 1 gives `0.5`; dimension 2 gives `½(0 + 1 − 0 − 1) = 0`. Total `0.5`.
4. `σ − 1/σ = 0` ⇔ `σ² = 1` ⇔ `σ = 1` for `σ > 0`.

---

## Verification

Checked with SymPy 1.14 in the project venv (script kept outside the repo):

- Integral form of KL equals the closed form (difference simplifies to `0`).
- Exercise 1 value `0.5`; `μ=0, σ=1` gives `0`.
- `∂f/∂μ = μ`; `∂f/∂σ = σ − 1/σ`; the only positive stationary `σ` is `1`.

Not checked: the multi-dimensional factorization (Step 7) and the non-negativity inequality (Step 6). Both are marked **[REVIEW]**.

## References

- Kingma, D. P., & Welling, M. (2013). Auto-encoding variational Bayes. arXiv:1312.6114. (Appendix B gives the Gaussian KL.) **[REVIEW]** confirm the appendix reference before final.
