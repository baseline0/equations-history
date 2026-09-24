"""Loss function equations: cross-entropy, KL divergence, and Wasserstein distance.

Source of truth for loss function mathematical definitions. Each equation
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


class LossFunctionEquations:
    """Loss function definitions: cross-entropy, KL divergence, and Wasserstein."""

    # Symbols (source: loss_functions.py:30)
    y = sp.Symbol("y", real=True)  # True label (or distribution)
    y_hat = sp.Symbol(r"\hat{y}", real=True)  # Predicted label (or distribution)
    p = sp.Symbol("p", real=True, positive=True)  # Probability distribution
    q = sp.Symbol("q", real=True, positive=True)  # Predicted probability distribution
    x = sp.Symbol("x", real=True)  # Input
    N = sp.Symbol("N", real=True, positive=True, integer=True)  # Number of samples
    C = sp.Symbol("C", real=True, positive=True, integer=True)  # Number of classes
    K = sp.Symbol("K", real=True, positive=True, integer=True)  # Number of samples (Wasserstein)

    @staticmethod
    def cross_entropy_binary() -> Equation:
        """Binary Cross-Entropy: classification loss for binary outcomes.

        Measures divergence between predicted and true binary probabilities.
        Commonly used for binary classification and sigmoid-activated outputs.

        Source: loss_functions.py:40
        """
        return Equation(
            name="Binary Cross-Entropy Loss",
            latex=(
                r"\mathcal{L}_{\text{BCE}} = -\frac{1}{N} \sum_{i=1}^{N} "
                r"[y_i \log \hat{y}_i + (1 - y_i) \log(1 - \hat{y}_i)]"
            ),
            description=(
                "Average negative log-likelihood for binary classification. "
                "y ∈ {0, 1}, ŷ ∈ (0, 1) is predicted probability."
            ),
            history=(
                "Cross-entropy as a loss function stems from information theory (Shannon, 1948). "
                "In machine learning, it represents the expected number of bits needed to encode "
                "samples from the true distribution using a code optimized for the predicted distribution. "
                "For binary classification, BCE is the maximum-likelihood estimator under the assumption "
                "that true labels follow a Bernoulli distribution with probability ŷ. "
                "BCE became standard in neural networks when combined with sigmoid output activations."
            ),
            citations=[
                "Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27, 379-423.",
                "Bishop, C. M. (2006). Pattern Recognition and Machine Learning. Springer.",
                "LeCun, Y., Bottou, L., Orr, G. B., & Müller, K. R. (1998). Efficient BackProp. "
                "In Neural Networks: Tricks of the Trade.",
            ],
            source_line=40,
            concepts=["cross-entropy", "binary classification", "maximum likelihood", "logarithmic loss"],
        )

    @staticmethod
    def cross_entropy_multiclass() -> Equation:
        """Categorical Cross-Entropy: classification loss for multi-class problems.

        Measures divergence between predicted and true categorical distributions.
        Commonly used with softmax output activations.

        Source: loss_functions.py:60
        """
        return Equation(
            name="Categorical Cross-Entropy Loss",
            latex=(
                r"\mathcal{L}_{\text{CCE}} = -\frac{1}{N} \sum_{i=1}^{N} \sum_{c=1}^{C} "
                r"y_{i,c} \log \hat{y}_{i,c}"
            ),
            description=(
                "Average negative log-likelihood for K-class classification. "
                "y is one-hot encoded true label; ŷ is softmax probability vector."
            ),
            history=(
                "Categorical cross-entropy extends binary cross-entropy to multiple classes. "
                "It is the maximum-likelihood loss for categorical outcomes modeled as softmax distributions. "
                "The one-hot encoding of y means only the true class contributes to the sum. "
                "This loss became standard in deep learning for multi-class problems (e.g., ImageNet classification). "
                "Its relationship to cross-entropy ensures well-calibrated probabilities."
            ),
            citations=[
                "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press. Chapter 6.",
                "Bishop, C. M. (2006). Pattern Recognition and Machine Learning. Springer.",
            ],
            source_line=60,
            concepts=["categorical cross-entropy", "multi-class classification", "softmax", "maximum likelihood"],
        )

    @staticmethod
    def kl_divergence() -> Equation:
        """Kullback-Leibler (KL) Divergence: measure of probability distribution divergence.

        Measures how much one probability distribution differs from another.
        Used in variational inference and information theory.

        Source: loss_functions.py:80
        """
        return Equation(
            name="Kullback-Leibler Divergence",
            latex=(
                r"\mathrm{KL}(p \| q) = \sum_x p(x) \log \frac{p(x)}{q(x)} = "
                r"\mathbb{E}_{x \sim p}\left[\log p(x) - \log q(x)\right]"
            ),
            description=(
                "Expected log-ratio of true and predicted probabilities. "
                "Non-negative; zero only when p = q."
            ),
            history=(
                "KL divergence was introduced by Kullback & Leibler (1951) in information theory. "
                "It measures how much information is lost when approximating true distribution p "
                "with approximate distribution q. KL divergence is asymmetric: KL(p||q) ≠ KL(q||p). "
                "In machine learning, KL(true||predicted) is the maximum-likelihood loss. "
                "In VAEs and other latent-variable models, KL regularizes the approximate posterior "
                "toward the prior. The non-negativity and zero-only-at-equality properties make it "
                "a natural distance-like measure between distributions."
            ),
            citations=[
                "Kullback, S., & Leibler, R. A. (1951). On information and sufficiency. "
                "Annals of Mathematical Statistics, 22(1), 79-86.",
                "Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory (2nd ed.). Wiley-Interscience.",
            ],
            source_line=80,
            concepts=["KL divergence", "relative entropy", "information theory", "distribution divergence"],
        )

    @staticmethod
    def jensen_shannon_divergence() -> Equation:
        """Jensen-Shannon Divergence: symmetric, bounded KL divergence.

        Symmetric version of KL divergence; ranges from 0 to 1 (in bits).
        Used when asymmetry of KL is undesirable.

        Source: loss_functions.py:105
        """
        return Equation(
            name="Jensen-Shannon Divergence",
            latex=(
                r"\mathrm{JS}(p \| q) = \frac{1}{2} \mathrm{KL}(p \| m) + \frac{1}{2} \mathrm{KL}(q \| m), "
                r"\quad m = \frac{p + q}{2}"
            ),
            description=(
                "Symmetric divergence: average KL from each distribution to their mean m. "
                "Always well-defined and symmetric: JS(p||q) = JS(q||p)."
            ),
            history=(
                "Jensen-Shannon divergence was introduced by Lin (1991) as a symmetric alternative to KL. "
                "By comparing each distribution to their average m = (p+q)/2, it avoids KL's asymmetry. "
                "The square root of JS divergence is a true metric (satisfies triangle inequality). "
                "JS is more interpretable for applications requiring symmetry, such as comparing two models. "
                "However, it is more expensive to compute than KL and is less commonly used in deep learning."
            ),
            citations=[
                "Lin, J. (1991). Divergence measures based on the Shannon entropy. "
                "IEEE Transactions on Information Theory, 37(1), 145-151.",
                "Endres, D. M., & Schindelin, J. E. (2003). A new metric for probability distributions. "
                "IEEE Transactions on Information Theory, 49(7), 1858-1860.",
            ],
            source_line=105,
            concepts=["Jensen-Shannon divergence", "symmetric divergence", "metric", "distribution comparison"],
        )

    @staticmethod
    def wasserstein_distance() -> Equation:
        """Wasserstein Distance (Optimal Transport): Earth Mover's Distance.

        Minimum cost to transform one probability distribution into another.
        Geometrically motivated; more stable gradients than KL.

        Source: loss_functions.py:130
        """
        return Equation(
            name="Wasserstein Distance (1-Wasserstein)",
            latex=(
                r"W_1(p, q) = \inf_{\gamma} \mathbb{E}_{(x,y) \sim \gamma}[\|x - y\|] = "
                r"\inf_{\gamma} \int \|x - y\| \, d\gamma(x, y)"
            ),
            description=(
                "Minimum cost (expected distance) to transport mass from p to q. "
                "Infimum over all couplings γ with marginals p and q."
            ),
            history=(
                "Wasserstein distance originates from optimal transport theory (Monge, 1781; Kantorovich, 1942). "
                "It measures the minimum cost to move probability mass from one distribution to another. "
                "Unlike KL divergence, Wasserstein distance provides meaningful gradients even when "
                "p and q have non-overlapping support (e.g., disjoint point masses). "
                "In deep learning, Wasserstein distance enabled Wasserstein GANs (Arjovsky et al., 2017), "
                "which provide more stable training than KL-based GANs. The geometric intuition—moving mass "
                "over space—makes Wasserstein distance more interpretable than KL for distribution learning."
            ),
            citations=[
                "Monge, G. (1781). Mémoire sur la théorie des déblais et des remblais. "
                "L'Académie Royale des Sciences de Paris.",
                "Kantorovich, L. V. (1942). On the translocation of masses. "
                "C. R. (Doklady) Acad. Sci. USSR, 37, 199-201.",
                "Arjovsky, M., Chintala, S., & Bottou, L. (2017). Wasserstein GAN. arXiv:1701.07875.",
                "Villani, C. (2008). Optimal Transport: Old and New. Springer-Verlag.",
            ],
            source_line=130,
            concepts=["Wasserstein distance", "optimal transport", "Earth Mover's Distance", "coupling"],
        )

    @staticmethod
    def earth_mover_distance_discrete() -> Equation:
        """Wasserstein Distance for discrete distributions: EMD approximation.

        Practical computation of Wasserstein distance for finite sample sets
        using assignment/flow optimization.

        Source: loss_functions.py:155
        """
        return Equation(
            name="Earth Mover's Distance (Discrete Approximation)",
            latex=(
                r"W_p(P, Q) \approx \left( \min_{\phi \in \mathrm{bijections}} "
                r"\sum_{i=1}^{K} \|x_i - y_{\phi(i)}\|^p \right)^{1/p}"
            ),
            description=(
                "Discrete approximation: minimum cost assignment between two point sets. "
                "φ is a permutation; K is the number of samples."
            ),
            history=(
                "For finite point sets, Wasserstein distance reduces to an optimal assignment problem: "
                "find a bijection φ that minimizes the total cost of matching points between the two sets. "
                "This discrete version is computationally tractable via the Hungarian algorithm (O(K³)). "
                "However, computing true Wasserstein distance remains expensive for large sets. "
                "Sliced Wasserstein distance (Radon transform) and other approximations provide faster alternatives. "
                "Despite computational cost, Wasserstein distance's geometric stability has made it influential "
                "in generative modeling and domain adaptation."
            ),
            citations=[
                "Kuhn, H. W. (1955). The Hungarian method for the assignment problem. "
                "Naval Research Logistics Quarterly, 2(1-2), 83-97.",
                "Kolouri, S., Park, S. R., Thorpe, M., Slepčev, D., & Rohde, G. K. (2017). "
                "Optimal mass transport: Signal processing and machine-learning applications. arXiv:1612.02964.",
            ],
            source_line=155,
            concepts=["Wasserstein distance", "discrete approximation", "optimal assignment", "Hungarian algorithm"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all loss function equations."""
    return {
        "cross_entropy_binary": LossFunctionEquations.cross_entropy_binary(),
        "cross_entropy_multiclass": LossFunctionEquations.cross_entropy_multiclass(),
        "kl_divergence": LossFunctionEquations.kl_divergence(),
        "jensen_shannon_divergence": LossFunctionEquations.jensen_shannon_divergence(),
        "wasserstein_distance": LossFunctionEquations.wasserstein_distance(),
        "earth_mover_distance_discrete": LossFunctionEquations.earth_mover_distance_discrete(),
    }
