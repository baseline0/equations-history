"""Autoencoder equations: standard and variational.

Source of truth for autoencoder mathematical definitions. Each equation
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


class AutoencoderEquations:
    """Autoencoder definitions: deterministic and variational."""

    # Symbols (source: autoencoders.py:30)
    x = sp.Symbol("x", real=True)  # Input vector
    z = sp.Symbol("z", real=True)  # Latent code
    x_hat = sp.Symbol(r"\hat{x}", real=True)  # Reconstructed output
    phi = sp.Symbol("phi", real=True)  # Encoder parameters
    theta = sp.Symbol("theta", real=True)  # Decoder parameters
    W_e = sp.Symbol("W_e", real=False)  # Encoder weights
    b_e = sp.Symbol("b_e", real=False)  # Encoder bias
    W_d = sp.Symbol("W_d", real=False)  # Decoder weights
    b_d = sp.Symbol("b_d", real=False)  # Decoder bias

    @staticmethod
    def deterministic_encoder() -> Equation:
        """Deterministic encoder: z = f_φ(x).

        The encoder maps input x to latent code z via a parameterized function.
        In practice, this is a neural network with weights φ.

        Source: autoencoders.py:40
        """
        # Symbolic form (simplified): z = σ(W_e * x + b_e)
        sigma = sp.Function("sigma")  # Activation function placeholder
        encoder_expr = sigma(AutoencoderEquations.W_e * AutoencoderEquations.x + AutoencoderEquations.b_e)

        return Equation(
            name="Deterministic Encoder",
            latex=r"z = f_\phi(x)",
            description="Encoder maps input x to latent code z",
            history=(
                "Autoencoders trace back to Rumelhart et al. (1986) and were popularized "
                "by Hinton & Salakhutdinov (2006) for dimensionality reduction. "
                "The encoder-decoder bottleneck forces the network to learn compressed representations."
            ),
            citations=[
                "Hinton, G. E., & Salakhutdinov, R. R. (2006). "
                "Reducing the dimensionality of data with neural networks. Science.",
                "Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). "
                "Learning representations by back-propagating errors. Nature.",
            ],
            source_line=40,
            concepts=["encoder", "bottleneck", "dimensionality reduction"],
        )

    @staticmethod
    def deterministic_decoder() -> Equation:
        """Deterministic decoder: x̂ = g_θ(z).

        The decoder reconstructs input from latent code z.

        Source: autoencoders.py:55
        """
        sigma = sp.Function("sigma")
        decoder_expr = sigma(AutoencoderEquations.W_d * AutoencoderEquations.z + AutoencoderEquations.b_d)

        return Equation(
            name="Deterministic Decoder",
            latex=r"\hat{x} = g_\theta(z)",
            description="Decoder reconstructs input x from latent code z",
            history=(
                "The decoder mirrors the encoder architecture. Together they form "
                "the autoencoder bottleneck: information must flow through the small "
                "latent dimension z, forcing compression."
            ),
            citations=[
                "LeCun, Y., Bengio, Y., & Hinton, G. (2015). "
                "Deep learning. Nature, 521(7553), 436-444."
            ],
            source_line=55,
            concepts=["decoder", "reconstruction", "symmetry"],
        )

    @staticmethod
    def mse_reconstruction_loss() -> Equation:
        """Mean Squared Error reconstruction loss.

        For real-valued inputs (e.g., images), measure reconstruction error as MSE.

        Source: autoencoders.py:70
        """
        mse = sp.Rational(1, 2) * (AutoencoderEquations.x - AutoencoderEquations.x_hat) ** 2

        return Equation(
            name="MSE Reconstruction Loss",
            latex=r"\mathcal{L}_\text{MSE}(x, \hat{x}) = \frac{1}{2} \|x - \hat{x}\|_2^2",
            description="Quadratic error between input and reconstruction",
            history=(
                "MSE is the canonical loss for autoencoders on continuous data. "
                "It penalizes large errors quadratically, encouraging precise reconstruction. "
                "Commonly used for image autoencoders."
            ),
            citations=[
                "Goodfellow, I., Bengio, Y., & Courville, A. (2016). "
                "Deep Learning. MIT Press. Chapter 14 (Autoencoders)."
            ],
            source_line=70,
            concepts=["loss", "reconstruction error", "continuous data"],
        )

    @staticmethod
    def bce_reconstruction_loss() -> Equation:
        """Binary Cross-Entropy reconstruction loss.

        For binary/normalized inputs (e.g., pixel values in [0,1]), use BCE.

        Source: autoencoders.py:85
        """
        # BCE: -sum(x * log(x_hat) + (1-x) * log(1-x_hat))
        bce_expr = -(
            AutoencoderEquations.x * sp.log(AutoencoderEquations.x_hat)
            + (1 - AutoencoderEquations.x) * sp.log(1 - AutoencoderEquations.x_hat)
        )

        return Equation(
            name="Binary Cross-Entropy Loss",
            latex=r"\mathcal{L}_\text{BCE}(x, \hat{x}) = -\sum_i [x_i \log \hat{x}_i + (1-x_i)\log(1-\hat{x}_i)]",
            description="Cross-entropy error for binary/normalized inputs",
            history=(
                "BCE is natural for classification-like tasks where each dimension "
                "represents a probability. Used in autoencoders for pixel-level reconstruction "
                "when data is normalized to [0,1]."
            ),
            citations=[
                "Bishop, C. M. (2006). Pattern Recognition and Machine Learning. "
                "Springer. Chapter 5 (Neural Networks)."
            ],
            source_line=85,
            concepts=["loss", "cross-entropy", "binary data"],
        )

    @staticmethod
    def vae_elbo() -> Equation:
        """Variational Autoencoder: Evidence Lower Bound (ELBO).

        The VAE optimizes a variational lower bound on log-likelihood.

        Source: autoencoders.py:105
        """
        return Equation(
            name="VAE ELBO (Evidence Lower Bound)",
            latex=(
                r"\text{ELBO}(x) = \mathbb{E}_{q_\phi(z|x)}\big[\log p_\theta(x|z)\big] "
                r"- \mathrm{KL}\big(q_\phi(z|x) \| p(z)\big)"
            ),
            description=(
                "Variational lower bound on log p(x). "
                "Reconstruction term (left) + regularization term (KL divergence, right)."
            ),
            history=(
                "VAEs were introduced by Kingma & Welling (2013) and independently "
                "by Rezende et al. (2014). They enable tractable learning of latent variable models "
                "by treating latent codes as random variables and optimizing a lower bound. "
                "The KL term shapes the latent distribution toward a prior, enabling generation and interpolation."
            ),
            citations=[
                "Kingma, D. P., & Welling, M. (2013). "
                "Auto-encoding variational Bayes. arXiv:1312.6114.",
                "Rezende, D. J., Mohamed, S., & Wierstra, D. (2014). "
                "Stochastic backpropagation and approximate inference in deep generative models. ICML.",
            ],
            source_line=105,
            concepts=["VAE", "generative model", "variational inference", "ELBO"],
        )

    @staticmethod
    def vae_kl_divergence_gaussian() -> Equation:
        """VAE KL divergence for Gaussian encoder and prior.

        Closed-form KL(q_φ(z|x) || p(z)) when both are Gaussians.

        Source: autoencoders.py:125
        """
        return Equation(
            name="VAE KL Divergence (Gaussian)",
            latex=(
                r"\mathrm{KL}\big(q_\phi(z|x) \| p(z)\big) = "
                r"\frac{1}{2}\sum_j \left( \mu_{\phi,j}^2 + \sigma_{\phi,j}^2 - \log \sigma_{\phi,j}^2 - 1 \right)"
            ),
            description=(
                "Closed-form KL divergence between encoder q_φ(z|x) = N(μ_φ(x), diag(σ²_φ(x))) "
                "and prior p(z) = N(0, I)."
            ),
            history=(
                "The closed-form KL for Gaussians is a key technical contribution of VAEs. "
                "It allows gradient-based optimization without approximating the divergence. "
                "The KL regularization encourages the learned latent distribution to stay close "
                "to the prior, which is essential for generation and latent interpolation."
            ),
            citations=[
                "Kingma, D. P., & Welling, M. (2013). "
                "Auto-encoding variational Bayes. arXiv:1312.6114.",
            ],
            source_line=125,
            concepts=["KL divergence", "Gaussian", "regularization", "latent distribution"],
        )

    @staticmethod
    def reparameterization_trick() -> Equation:
        """Reparameterization trick: enable gradient flow through sampling.

        z = μ(x) + σ(x) ⊙ ε, where ε ~ N(0, I).

        Source: autoencoders.py:145
        """
        return Equation(
            name="Reparameterization Trick",
            latex=r"z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)",
            description=(
                "Rewrite sampling as a deterministic function plus noise. "
                "Allows backpropagation through the sampling step."
            ),
            history=(
                "The reparameterization trick (Kingma & Welling, 2013) solves a fundamental issue: "
                "sampling is not differentiable, so gradients cannot flow through random nodes. "
                "By rewriting z = μ + σ⊙ε, we move the randomness to the input ε (which doesn't depend on parameters), "
                "making z differentiable w.r.t. μ and σ. This enables end-to-end training of VAEs."
            ),
            citations=[
                "Kingma, D. P., & Welling, M. (2013). "
                "Auto-encoding variational Bayes. arXiv:1312.6114."
            ],
            source_line=145,
            concepts=["gradient flow", "sampling", "backpropagation", "stochastic"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all autoencoder equations."""
    return {
        "deterministic_encoder": AutoencoderEquations.deterministic_encoder(),
        "deterministic_decoder": AutoencoderEquations.deterministic_decoder(),
        "mse_reconstruction_loss": AutoencoderEquations.mse_reconstruction_loss(),
        "bce_reconstruction_loss": AutoencoderEquations.bce_reconstruction_loss(),
        "vae_elbo": AutoencoderEquations.vae_elbo(),
        "vae_kl_divergence_gaussian": AutoencoderEquations.vae_kl_divergence_gaussian(),
        "reparameterization_trick": AutoencoderEquations.reparameterization_trick(),
    }
