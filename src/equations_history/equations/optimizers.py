"""Optimizer equations: SGD, momentum, and Adam.

Source of truth for optimizer mathematical definitions. Each equation
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


class OptimizerEquations:
    """Optimizer definitions: stochastic gradient descent, momentum, and Adam."""

    # Symbols (source: optimizers.py:30)
    theta = sp.Symbol("theta", real=True)  # Parameters
    theta_t = sp.Symbol(r"\theta_t", real=True)  # Parameters at step t
    g_t = sp.Symbol("g_t", real=True)  # Gradient at step t
    alpha = sp.Symbol("alpha", real=True, positive=True)  # Learning rate
    m_t = sp.Symbol("m_t", real=True)  # First moment (momentum)
    v_t = sp.Symbol("v_t", real=True)  # Second moment (variance)
    beta1 = sp.Symbol("beta_1", real=True, positive=True)  # Exponential decay rate 1
    beta2 = sp.Symbol("beta_2", real=True, positive=True)  # Exponential decay rate 2
    epsilon = sp.Symbol("epsilon", real=True, positive=True)  # Small constant for numerical stability

    @staticmethod
    def sgd_update() -> Equation:
        """Stochastic Gradient Descent (SGD) update rule.

        The most basic optimization algorithm: subtract the gradient scaled by learning rate.

        Source: optimizers.py:40
        """
        return Equation(
            name="Stochastic Gradient Descent (SGD)",
            latex=r"\theta_{t+1} = \theta_t - \alpha g_t",
            description="Update parameters by subtracting scaled gradient",
            history=(
                "SGD traces back to Robbins & Monro (1951) on stochastic approximation. "
                "In deep learning, Rumelhart et al. (1986) popularized it for backpropagation. "
                "SGD remains the foundational optimizer: simple, computationally efficient, and theoretically understood. "
                "Despite its simplicity, SGD often achieves excellent generalization on large-scale problems."
            ),
            citations=[
                "Robbins, H., & Monro, S. (1951). A stochastic approximation method. "
                "Annals of Mathematical Statistics, 22(3), 400-407.",
                "Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). "
                "Learning representations by back-propagating errors. Nature, 323, 533-536.",
                "LeCun, Y., Bottou, L., Orr, G. B., & Müller, K. R. (1998). "
                "Efficient BackProp. In Neural Networks: Tricks of the Trade.",
            ],
            source_line=40,
            concepts=["optimizer", "gradient descent", "stochastic", "learning rate"],
        )

    @staticmethod
    def momentum_update() -> Equation:
        """Momentum: accumulate exponential moving average of gradients.

        Accelerates convergence by maintaining a velocity term that builds up
        in consistent descent directions.

        Source: optimizers.py:60
        """
        return Equation(
            name="Momentum Update",
            latex=(
                r"m_t = \beta m_{t-1} + (1 - \beta) g_t \\ "
                r"\theta_{t+1} = \theta_t - \alpha m_t"
            ),
            description=(
                "Maintain exponential moving average of gradients; update with scaled momentum. "
                "Typical β ≈ 0.9."
            ),
            history=(
                "Momentum was introduced by Qian (1999) and has been a standard technique "
                "in deep learning since early 2000s. It addresses a key limitation of SGD: "
                "oscillations in directions with high curvature. By accumulating gradients, "
                "momentum smooths the optimization trajectory and often converges faster. "
                "Polyak's heavy-ball method (1964) provides theoretical foundation."
            ),
            citations=[
                "Qian, N. (1999). On the momentum term in gradient descent learning algorithms. "
                "Neural Networks, 12(1), 145-151.",
                "Polyak, B. T. (1964). Some methods of speeding up the convergence of iteration methods. "
                "USSR Computational Mathematics and Mathematical Physics, 4(5), 1-17.",
                "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press. Chapter 8.",
            ],
            source_line=60,
            concepts=["momentum", "exponential moving average", "acceleration", "convergence"],
        )

    @staticmethod
    def nesterov_momentum() -> Equation:
        """Nesterov Momentum: look ahead before applying gradient.

        Compute gradient at a point ahead in momentum direction,
        providing better curvature awareness.

        Source: optimizers.py:80
        """
        return Equation(
            name="Nesterov Momentum",
            latex=(
                r"\tilde{\theta}_t = \theta_t - \alpha m_{t-1} \\ "
                r"m_t = \beta m_{t-1} + (1 - \beta) g(\tilde{\theta}_t) \\ "
                r"\theta_{t+1} = \theta_t - \alpha m_t"
            ),
            description=(
                "Evaluate gradient at a point ahead in the momentum direction. "
                "Provides better convergence rate than standard momentum."
            ),
            history=(
                "Nesterov accelerated gradient was introduced by Nesterov (1983) with "
                "theoretical convergence rate O(1/k²) for convex problems. "
                "Adapted to SGD by Sutskever et al. (2013), it became essential in deep learning. "
                "The key insight: look ahead before computing gradients, providing better optimization geometry."
            ),
            citations=[
                "Nesterov, Y. (1983). A method for solving a convex programming problem with convergence rate O(1/k²). "
                "Soviet Mathematics Doklady, 27, 372-376.",
                "Sutskever, I., Martens, J., Dahl, G., & Hinton, G. (2013). "
                "On the importance of initialization and momentum in deep learning. ICML.",
            ],
            source_line=80,
            concepts=["Nesterov", "look-ahead", "momentum", "acceleration"],
        )

    @staticmethod
    def adam_biased_moments() -> Equation:
        """Adam: biased first and second moment estimates.

        Maintain exponential moving averages of gradients (first moment)
        and squared gradients (second moment).

        Source: optimizers.py:105
        """
        return Equation(
            name="Adam Moment Estimates (Biased)",
            latex=(
                r"m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t \\ "
                r"v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2"
            ),
            description=(
                "Update biased first moment (momentum) and second moment (variance) estimates. "
                "Typical β₁ ≈ 0.9, β₂ ≈ 0.999."
            ),
            history=(
                "These moment estimates form the core of Adam (Kingma & Ba, 2014). "
                "First moment m_t tracks gradient direction (like momentum). "
                "Second moment v_t tracks gradient magnitude, enabling adaptive per-parameter learning rates. "
                "Adam combines benefits of momentum and RMSprop."
            ),
            citations=[
                "Kingma, D. P., & Ba, J. (2014). Adam: A method for stochastic optimization. arXiv:1412.6980.",
            ],
            source_line=105,
            concepts=["Adam", "moment estimate", "adaptive learning rate", "exponential moving average"],
        )

    @staticmethod
    def adam_bias_correction() -> Equation:
        """Adam: bias correction for moment estimates.

        Correct for initialization bias in early iterations since moments
        start at zero.

        Source: optimizers.py:125
        """
        return Equation(
            name="Adam Bias Correction",
            latex=(
                r"\hat{m}_t = \frac{m_t}{1 - \beta_1^t} \\ "
                r"\hat{v}_t = \frac{v_t}{1 - \beta_2^t}"
            ),
            description=(
                "Bias-corrected moment estimates. Counteracts initialization bias. "
                "More important in early iterations; effect diminishes as t increases."
            ),
            history=(
                "Bias correction addresses a key issue: m_t and v_t are initialized to zero, "
                "biasing estimates downward early in training. The correction term (1 - β_t) "
                "scales moments up in early iterations, making them unbiased estimates of the true "
                "gradient and squared-gradient statistics. This ensures Adam's step sizes are reasonable "
                "from iteration 1 onwards (Kingma & Ba, 2014)."
            ),
            citations=[
                "Kingma, D. P., & Ba, J. (2014). Adam: A method for stochastic optimization. arXiv:1412.6980.",
            ],
            source_line=125,
            concepts=["bias correction", "initialization bias", "unbiased estimator"],
        )

    @staticmethod
    def adam_update() -> Equation:
        """Adam: parameter update with adaptive learning rate.

        Final update rule using bias-corrected moments and per-parameter
        adaptive learning rate.

        Source: optimizers.py:145
        """
        return Equation(
            name="Adam Parameter Update",
            latex=(
                r"\theta_{t+1} = \theta_t - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}"
            ),
            description=(
                "Update parameters with learning rate scaled by normalized second moment. "
                "Provides per-parameter adaptive learning rates and momentum simultaneously."
            ),
            history=(
                "The Adam update combines: (1) momentum via m_t, (2) adaptive per-parameter learning "
                "via 1/√(v_t), and (3) bias correction for reliable early iterations. "
                "The denominator √(v_t) + ε is key: parameters with high gradient variance "
                "get smaller effective learning rates, while stable parameters get larger steps. "
                "This balances exploration (momentum) with per-parameter adaptation. "
                "Adam became dominant in deep learning due to excellent empirical performance across tasks."
            ),
            citations=[
                "Kingma, D. P., & Ba, J. (2014). Adam: A method for stochastic optimization. arXiv:1412.6980.",
                "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press. Chapter 8.",
            ],
            source_line=145,
            concepts=["Adam", "adaptive learning rate", "per-parameter scaling", "parameter update"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all optimizer equations."""
    return {
        "sgd_update": OptimizerEquations.sgd_update(),
        "momentum_update": OptimizerEquations.momentum_update(),
        "nesterov_momentum": OptimizerEquations.nesterov_momentum(),
        "adam_biased_moments": OptimizerEquations.adam_biased_moments(),
        "adam_bias_correction": OptimizerEquations.adam_bias_correction(),
        "adam_update": OptimizerEquations.adam_update(),
    }
