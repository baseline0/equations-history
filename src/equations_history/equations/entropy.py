"""Entropy and information equations: entropy, conditional entropy, joint entropy,
mutual information, relative entropy (KL divergence), and Jensen's inequality.

Source of truth for information-theoretic definitions. Each equation includes
narrative context (history, citations, practical use cases).
"""

from equations_history.core import Equation

COVER_THOMAS = "Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory (2nd ed.). Wiley."


class EntropyEquations:
    """Entropy and information definitions: H, H(X|Y), H(X,Y), I(X;Y), D(P||Q), Jensen."""

    @staticmethod
    def entropy() -> Equation:
        """Shannon entropy: expected surprisal of a discrete random variable X.

        Source: entropy.py:31
        """
        return Equation(
            id="entropy.entropy",
            name="Entropy",
            latex=r"H(X) = -\sum_x p(x) \log p(x)",
            description=(
                "Expected surprisal (in nats for natural log, bits for log base 2) of a discrete "
                "random variable. Zero for a deterministic outcome; maximal for the uniform distribution."
            ),
            history=(
                "Shannon (1948) introduced entropy as a measure of information and uncertainty "
                "in A Mathematical Theory of Communication."
            ),
            citations=[COVER_THOMAS],
            concepts=["entropy", "information theory", "uncertainty", "surprisal"],
        )

    @staticmethod
    def conditional_entropy() -> Equation:
        """Conditional entropy: remaining uncertainty in X once Y is known.

        Source: entropy.py:53
        """
        return Equation(
            id="entropy.conditional_entropy",
            name="Conditional Entropy",
            latex=r"H(X \mid Y) = -\sum_{x,y} p(x,y) \log p(x \mid y)",
            description=(
                "Expected entropy of X given Y, averaged over Y. Equals H(X,Y) - H(Y) and is never larger than H(X)."
            ),
            history=(
                "Conditional entropy follows directly from Shannon's (1948) entropy definition. "
                "It is the quantity that the chain rule H(X,Y) = H(Y) + H(X|Y) decomposes into."
            ),
            citations=[COVER_THOMAS],
            concepts=["conditional entropy", "information theory", "chain rule"],
        )

    @staticmethod
    def joint_entropy() -> Equation:
        """Joint entropy: uncertainty of the pair (X, Y).

        Source: entropy.py:74
        """
        return Equation(
            id="entropy.joint_entropy",
            name="Joint Entropy",
            latex=r"H(X,Y) = -\sum_{x,y} p(x,y) \log p(x,y)",
            description=(
                "Entropy of the joint distribution of two random variables. "
                "Satisfies H(X,Y) = H(X) + H(Y|X) and is at most H(X) + H(Y)."
            ),
            history=(
                "Joint entropy extends Shannon's (1948) entropy to pairs of random variables. "
                "The chain rule H(X,Y) = H(X) + H(Y|X) is the basis for the decompositions used "
                "in information theory."
            ),
            citations=[COVER_THOMAS],
            concepts=["joint entropy", "information theory", "chain rule"],
        )

    @staticmethod
    def mutual_information() -> Equation:
        """Mutual information: reduction in uncertainty of X from knowing Y.

        Source: entropy.py:97
        """
        return Equation(
            id="entropy.mutual_information",
            name="Mutual Information",
            latex=(r"I(X;Y) = H(X) - H(X \mid Y) = \sum_{x,y} p(x,y) \log \frac{p(x,y)}{p(x)\,p(y)}"),
            description=(
                "Shared information between X and Y. Non-negative, symmetric, and zero "
                "exactly when X and Y are independent."
            ),
            history=(
                "Shannon (1948) defined the information shared between channel input and output. "
                "Mutual information is the central quantity of the channel coding theorem and "
                "is later used in information bottleneck formulations."
            ),
            citations=[COVER_THOMAS],
            concepts=["mutual information", "information theory", "independence", "information bottleneck"],
        )

    @staticmethod
    def relative_entropy() -> Equation:
        """Relative entropy (KL divergence) between distributions P and Q.

        Source: entropy.py:120
        """
        return Equation(
            id="entropy.relative_entropy",
            name="Relative Entropy (KL Divergence)",
            latex=r"D(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)}",
            description=(
                "Expected log-ratio of P to Q under P. Non-negative, zero if and only if P = Q, "
                "and asymmetric: D(P||Q) differs from D(Q||P) in general."
            ),
            history=(
                "Kullback & Leibler (1951) introduced this divergence in On Information and Sufficiency "
                "as a generalization of Shannon's information measure."
            ),
            citations=[
                "Kullback, S., & Leibler, R. A. (1951). On information and sufficiency. "
                "The Annals of Mathematical Statistics, 22(1), 79-86.",
                COVER_THOMAS,
            ],
            concepts=["relative entropy", "KL divergence", "information theory", "non-negativity"],
        )

    @staticmethod
    def jensens_inequality() -> Equation:
        """Jensen's inequality: convex (concave) f applied to an expectation.

        Source: entropy.py:146
        """
        return Equation(
            id="entropy.jensens_inequality",
            name="Jensen's Inequality",
            latex=r"f\left(\mathbb{E}[X]\right) \le \mathbb{E}\left[f(X)\right] \quad (f \text{ convex})",
            description=(
                "For convex f, f of the mean is at most the mean of f. The inequality reverses for "
                "concave f, such as log. It underlies non-negativity of KL divergence and many variational bounds."
            ),
            history=(
                "Jensen (1906) proved the inequality for convex functions. It is the standard tool "
                "behind non-negativity of relative entropy and the variational lower bounds used in ML."
            ),
            citations=[
                "Jensen, J. L. W. V. (1906). Sur les fonctions convexes et les inégalités entre les valeurs "
                "moyennes. Acta Mathematica, 30, 175-193.",
                COVER_THOMAS,
            ],
            concepts=["Jensen's inequality", "convexity", "concavity", "expectation", "variational bound"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all entropy and information equations."""
    return {
        "entropy": EntropyEquations.entropy(),
        "conditional_entropy": EntropyEquations.conditional_entropy(),
        "joint_entropy": EntropyEquations.joint_entropy(),
        "mutual_information": EntropyEquations.mutual_information(),
        "relative_entropy": EntropyEquations.relative_entropy(),
        "jensens_inequality": EntropyEquations.jensens_inequality(),
    }
