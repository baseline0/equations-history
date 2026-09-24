"""Regularization equations: dropout, L2 penalty, and batch normalization.

Source of truth for regularization mathematical definitions. Each equation
includes narrative context (history, citations, practical use cases).
"""

import sympy as sp
from dataclasses import dataclass


@dataclass
class Equation:
    """Container for an equation with metadata."""
    name: str
    latex: str
    description: str
    history: str
    citations: list[str]
    source_line: int
    concepts: list[str]


class RegularizationEquations:
    """Regularization definitions: dropout, L2 penalty, and batch normalization."""

    # Symbols (source: regularization.py:30)
    x = sp.Symbol("x", real=True)  # Input
    y = sp.Symbol("y", real=True)  # Output
    L = sp.Symbol("L", real=True)  # Loss
    W = sp.Symbol("W", real=False)  # Weights
    p = sp.Symbol("p", real=True, positive=True)  # Dropout probability (retention rate)
    lambda_reg = sp.Symbol(r"\lambda", real=True, positive=True)  # Regularization coefficient
    mu = sp.Symbol("mu", real=True)  # Batch mean
    sigma = sp.Symbol("sigma", real=True, positive=True)  # Batch standard deviation
    gamma = sp.Symbol("gamma", real=True)  # Learnable scale parameter
    beta = sp.Symbol("beta", real=True)  # Learnable shift parameter
    epsilon = sp.Symbol("epsilon", real=True, positive=True)  # Small constant for numerical stability

    @staticmethod
    def dropout_training() -> Equation:
        """Dropout during training: randomly zero activations with probability (1-p).

        Randomly drop units to prevent co-adaptation and encourage redundancy
        in learned representations.

        Source: regularization.py:40
        """
        return Equation(
            name="Dropout (Training)",
            latex=(
                r"z = h \odot m, \quad m_i \sim \text{Bernoulli}(p) \\ "
                r"\hat{z} = \frac{z}{p}"
            ),
            description=(
                "Sample binary mask m with retention probability p. "
                "Scale output by 1/p (inverted dropout) to maintain expected value."
            ),
            history=(
                "Dropout was introduced by Hinton et al. (2012) as a powerful regularization technique. "
                "The key insight: training an ensemble of sub-networks (created by random dropout masks) "
                "and averaging predictions at test time approximates combining exponentially many models. "
                "Dropout prevents co-adaptation of features: neurons cannot rely on specific partners being present. "
                "This forces each neuron to learn robust, independent features. "
                "Inverted dropout (scaling by 1/p during training) maintains statistical properties."
            ),
            citations=[
                "Hinton, G. E., Srivastava, N., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. R. (2012). "
                "Improving neural networks by preventing co-adaptation of feature detectors. arXiv:1207.0580.",
                "Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014). "
                "Dropout: A simple way to prevent neural networks from overfitting. JMLR, 15, 1929-1958.",
            ],
            source_line=40,
            concepts=["dropout", "regularization", "ensemble", "co-adaptation", "inverted dropout"],
        )

    @staticmethod
    def dropout_inference() -> Equation:
        """Dropout at inference: use all units (expectation over ensemble).

        At test time, use all activations without dropout. This approximates
        averaging predictions from all sub-networks trained during dropout.

        Source: regularization.py:60
        """
        return Equation(
            name="Dropout (Inference)",
            latex=r"z_{\text{test}} = h",
            description="At inference: use all activations (no dropout). Approximates ensemble averaging.",
            history=(
                "During training, dropout creates an implicit ensemble where each minibatch "
                "corresponds to a different sub-network. At test time, using all units approximates "
                "computing the geometric mean of predictions from all sub-networks (Srivastava et al., 2014). "
                "This ensemble effect is central to dropout's regularization power: "
                "the model learns diverse, robust features because it cannot specialize on particular combinations."
            ),
            citations=[
                "Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014). "
                "Dropout: A simple way to prevent neural networks from overfitting. JMLR, 15, 1929-1958.",
            ],
            source_line=60,
            concepts=["dropout", "inference", "ensemble averaging", "test time"],
        )

    @staticmethod
    def l2_regularization() -> Equation:
        """L2 regularization (weight decay): penalize large weights.

        Add squared weight norm to loss to encourage small, distributed
        weight values and improve generalization.

        Source: regularization.py:80
        """
        return Equation(
            name="L2 Regularization (Weight Decay)",
            latex=(
                r"\mathcal{L}_{\text{reg}} = \mathcal{L}(y, \hat{y}) + \frac{\lambda}{2} \|W\|_2^2 = "
                r"\mathcal{L}(y, \hat{y}) + \frac{\lambda}{2} \sum_i W_i^2"
            ),
            description=(
                "Add squared L2 norm of weights to loss. Typical λ ≈ 1e-4 to 1e-2. "
                "Encourages weights toward zero without forcing sparsity."
            ),
            history=(
                "L2 regularization traces to Tikhonov regularization in classical numerical analysis (1963). "
                "In machine learning, it's a foundational technique for preventing overfitting. "
                "The squared penalty term λ/2 ||W||² encourages weights to stay small, which has multiple benefits: "
                "(1) reduces model complexity, (2) improves numerical stability, (3) implements implicit Gaussian prior on weights. "
                "Unlike L1 (lasso), L2 does not produce sparse solutions; instead, weight values are smoothly reduced. "
                "Also known as weight decay in SGD optimizers, L2 regularization is ubiquitous in deep learning."
            ),
            citations=[
                "Tikhonov, A. N. (1963). Solution of incorrectly formulated problems and the regularization method. "
                "Soviet Mathematics Doklady, 4, 1035-1038.",
                "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press. Chapter 5.",
                "LeCun, Y., Bottou, L., Orr, G. B., & Müller, K. R. (1998). Efficient BackProp. "
                "In Neural Networks: Tricks of the Trade.",
            ],
            source_line=80,
            concepts=["L2 regularization", "weight decay", "Tikhonov", "overfitting prevention"],
        )

    @staticmethod
    def batch_normalization_normalize() -> Equation:
        """Batch Normalization: normalize activations by batch statistics.

        Normalize layer inputs to zero mean and unit variance using
        batch statistics during training.

        Source: regularization.py:105
        """
        return Equation(
            name="Batch Normalization (Normalization)",
            latex=(
                r"\hat{x}_i = \frac{x_i - \mu_{\text{batch}}}{\sqrt{\sigma_{\text{batch}}^2 + \epsilon}}"
            ),
            description=(
                "Normalize using batch mean μ_batch and batch variance σ²_batch. "
                "Small ε prevents division by zero."
            ),
            history=(
                "Batch Normalization was introduced by Ioffe & Szegedy (2015) as a breakthrough technique. "
                "The core insight: reducing internal covariate shift (the change in activation distribution "
                "across layers) accelerates training and reduces sensitivity to weight initialization. "
                "By normalizing inputs to each layer, batch norm stabilizes gradients and allows higher learning rates. "
                "This dramatically accelerated training of deep networks."
            ),
            citations=[
                "Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training "
                "by reducing internal covariate shift. ICML.",
            ],
            source_line=105,
            concepts=["batch normalization", "normalization", "covariate shift", "standardization"],
        )

    @staticmethod
    def batch_normalization_scale_shift() -> Equation:
        """Batch Normalization: learnable affine transformation.

        Apply learnable scale and shift parameters to allow the network
        to undo normalization if beneficial.

        Source: regularization.py:125
        """
        return Equation(
            name="Batch Normalization (Scale and Shift)",
            latex=r"y_i = \gamma \hat{x}_i + \beta",
            description=(
                "Apply learnable scale γ and shift β. Allows network to learn "
                "the optimal level of normalization."
            ),
            history=(
                "The learnable parameters γ (scale) and β (shift) are crucial to batch norm's flexibility. "
                "Without them, normalization would force all activations into a standard Gaussian, "
                "potentially limiting model expressiveness. The γ and β parameters let each layer learn "
                "the optimal amount of normalization: if a layer needs strong signal variance, γ can scale it up; "
                "if it needs a shifted distribution, β can shift it. This design preserves the benefits of normalization "
                "while maintaining model capacity (Ioffe & Szegedy, 2015)."
            ),
            citations=[
                "Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training "
                "by reducing internal covariate shift. ICML.",
            ],
            source_line=125,
            concepts=["batch normalization", "learnable parameters", "scale", "shift", "affine transformation"],
        )

    @staticmethod
    def batch_normalization_inference() -> Equation:
        """Batch Normalization at inference: use running statistics.

        At test time, use exponential moving average of batch statistics
        accumulated during training instead of batch statistics.

        Source: regularization.py:145
        """
        return Equation(
            name="Batch Normalization (Inference)",
            latex=(
                r"\hat{x}_i = \frac{x_i - \mu_{\text{running}}}{\sqrt{\sigma_{\text{running}}^2 + \epsilon}}"
            ),
            description=(
                "Use running mean μ_running and running variance σ²_running. "
                "These are exponential moving averages updated during training."
            ),
            history=(
                "During training, batch norm normalizes by batch statistics. But at inference, "
                "there may be no batch (only a single example). Batch Normalization solves this by "
                "maintaining exponential moving averages (running mean and variance) throughout training. "
                "At test time, these running statistics replace the (unavailable or unreliable) batch statistics. "
                "This ensures batch norm can be applied at inference to single examples or small batches "
                "without degradation (Ioffe & Szegedy, 2015)."
            ),
            citations=[
                "Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training "
                "by reducing internal covariate shift. ICML.",
            ],
            source_line=145,
            concepts=["batch normalization", "inference", "running statistics", "exponential moving average"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all regularization equations."""
    return {
        "dropout_training": RegularizationEquations.dropout_training(),
        "dropout_inference": RegularizationEquations.dropout_inference(),
        "l2_regularization": RegularizationEquations.l2_regularization(),
        "batch_normalization_normalize": RegularizationEquations.batch_normalization_normalize(),
        "batch_normalization_scale_shift": RegularizationEquations.batch_normalization_scale_shift(),
        "batch_normalization_inference": RegularizationEquations.batch_normalization_inference(),
    }
