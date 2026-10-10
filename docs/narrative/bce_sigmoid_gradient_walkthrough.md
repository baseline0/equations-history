# Walkthrough: Why BCE with a sigmoid output gives gradient `x̂ − x`

> **DRAFT for human review.** Not finished. Algebra steps were checked with
> SymPy 1.14 (see "Verification"). Claims marked **[REVIEW]** need a human check.

**Setting:** an autoencoder decoder produces a logit `a` for one output unit; the reconstruction is `x̂ = σ(a) = 1/(1 + e^{−a})`. The target is `x ∈ {0, 1}` (or any `x ∈ [0, 1]`; the algebra does not depend on this). The loss is binary cross-entropy from `bce_reconstruction_loss` in `src/equations_history/equations/autoencoders.py`, for one dimension:

$$
L(a) = -\big[x\log\hat{x} + (1-x)\log(1-\hat{x})\big], \qquad \hat{x} = \sigma(a)
$$

**Target result:**

$$
\frac{\partial L}{\partial a} = \hat{x} - x
$$

---

## Steps

### Step 1: Derivative of the sigmoid

$$
\sigma'(a) = \frac{d}{da}\,(1+e^{-a})^{-1} = \frac{e^{-a}}{(1+e^{-a})^2}
$$

Since `1 − σ(a) = e^{−a}/(1+e^{−a})`, we get

$$
\sigma'(a) = \sigma(a)\big(1-\sigma(a)\big) = \hat{x}(1-\hat{x})
$$

**Verified:** SymPy confirms `d/da σ(a) − σ(a)(1−σ(a)) = 0`.

### Step 2: Derivative of the loss with respect to `x̂`

$$
\frac{\partial L}{\partial \hat{x}} = -\frac{x}{\hat{x}} + \frac{1-x}{1-\hat{x}}
$$

(Standard derivative of `log`; each term uses `d/du log u = 1/u` with the chain rule for `1−x̂`.)

### Step 3: Chain rule

$$
\frac{\partial L}{\partial a} = \frac{\partial L}{\partial \hat{x}}\cdot \frac{d\hat{x}}{da} = \left(-\frac{x}{\hat{x}} + \frac{1-x}{1-\hat{x}}\right)\hat{x}(1-\hat{x})
$$

### Step 4: Expand and cancel

Distribute the two terms:

- First term: `−(x/x̂) · x̂(1−x̂) = −x(1−x̂)`
- Second term: `((1−x)/(1−x̂)) · x̂(1−x̂) = (1−x)x̂`

Sum:

$$
-x(1-\hat{x}) + (1-x)\hat{x} = -x + x\hat{x} + \hat{x} - x\hat{x} = \hat{x} - x
$$

The `x·x̂` terms cancel. This is the target result. **Verified:** SymPy gives `∂L/∂a − (x̂ − x) = 0` symbolically.

### Step 5: Why this matters **[REVIEW]**

The gradient with respect to the logit is `x̂ − x`, with no `σ'(a)` factor. So the update is not damped when the output saturates. Contrast this with MSE, `½(x − x̂)²`, whose gradient with respect to `a` is `σ'(a)(x̂ − x)` (Step 1 used again). When `|a|` is large, `σ'(a)` is near zero and MSE learns slowly. **Verified** numerically at `a = −10, x = 1` (below). The "learns slowly" interpretation is an informal reading and needs reviewer sign-off.

---

## Exercises

1. Compute `∂L/∂a` at `x = 1, a = 0`.
2. For `x = 0, a = 10`, is the BCE gradient large or small? What does its sign tell gradient descent to do?
3. Compute the MSE gradient `∂/∂a ½(x − σ(a))²` at `x = 1, a = 0`.
4. Show that `∂L/∂a = 0` exactly when `x̂ = x`. (Assume `x ∈ {0, 1}`.)

## Answers

1. `x̂ − x = σ(0) − 1 = 0.5 − 1 = −0.5`.
2. `x̂ = σ(10) ≈ 0.99995`, so `x̂ − x ≈ 0.99995`. The gradient is large and positive, so gradient descent decreases `a`, moving `x̂` toward 0, which is the correct direction for target `x = 0`.
3. `σ'(0)·(σ(0) − 1) = 0.25 · (−0.5) = −0.125`.
4. With `x ∈ {0, 1}`, `x̂ − x = 0` means `x̂ = x`. For `x = 1` that requires `σ(a) = 1`, which has no finite solution in `a`; so the gradient is zero only in the limit `a → ∞`. **[REVIEW]** the exercise statement "exactly when" needs rewording: for `x ∈ {0,1}` it holds only as `|a| → ∞`, not at any finite logit. Consider reformulating as "for `x ∈ (0,1)`".

---

## Verification

Checked with SymPy 1.14 in the project venv (script kept outside the repo):

- `σ'(a) = σ(a)(1−σ(a))` (symbolic difference `0`).
- `∂L/∂a = x̂ − x` (symbolic difference `0`).
- Exercise 1 value `−0.5`.
- Exercise 3 MSE gradient at `a = −10, x = 1`: MSE gives `−4.5 × 10⁻⁵`, BCE gives `−0.99995`. Matches `σ'(a)(x̂ − x)` symbolically.
- Exercise 2 BCE gradient at `a = 10, x = 0`: `0.99995` (SymPy).
- Exercise 3 MSE gradient at `a = 0, x = 1`: `−1/8` (SymPy).

Not checked: the Step 5 interpretation. Exercise 4 is flagged **[REVIEW]**.

## References

- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. (Output units and cross-entropy losses, Ch. 6.) **[REVIEW]** confirm the chapter reference before final.
