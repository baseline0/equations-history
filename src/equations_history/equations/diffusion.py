"""Diffusion model equations: forward process, reverse process, and score matching.

Source of truth for diffusion model mathematical definitions. Each equation
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


class DiffusionEquations:
    """Diffusion model definitions: forward process, reverse process, score matching."""

    # Symbols (source: diffusion.py:30)
    x = sp.Symbol("x", real=True)  # Data (x_0)
    x_t = sp.Symbol("x_t", real=True)  # Noisy data at time t
    z = sp.Symbol("z", real=True)  # Standard Gaussian noise
    t = sp.Symbol("t", real=True, positive=True)  # Time step
    T = sp.Symbol("T", real=True, positive=True)  # Total time steps
    alpha_t = sp.Symbol(r"\alpha_t", real=True, positive=True)  # Cumulative product of alphas
    beta_t = sp.Symbol(r"\beta_t", real=True, positive=True)  # Noise schedule
    sigma_t = sp.Symbol(r"\sigma_t", real=True, positive=True)  # Noise level
    score = sp.Function("s")  # Score function (gradient of log probability)
    epsilon = sp.Symbol("epsilon", real=True)  # Predicted noise

    @staticmethod
    def forward_process_markov() -> Equation:
        """Diffusion forward process: Markov chain adding noise over T steps.

        Gradually add Gaussian noise to data according to a schedule β_t.
        At t=0: clean data; at t=T: pure noise.

        Source: diffusion.py:40
        """
        return Equation(
            name="Diffusion Forward Process (Markov)",
            latex=(
                r"q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1 - \beta_t} x_{t-1}, \beta_t I)"
            ),
            description=(
                "Each step: add noise with variance β_t while scaling previous state by √(1-β_t). "
                "Forms a Markov chain from x_0 (data) to x_T ≈ N(0,I) (noise)."
            ),
            history=(
                "The forward diffusion process was formalized in diffusion probabilistic models "
                "(Ho, Jain, Abbeel, 2020). It is inspired by physics (noise-induced transitions) "
                "and has roots in score-based generative modeling (Song & Ermon, 2019). "
                "The key insight: gradually adding noise converts complex data distributions to simple Gaussians. "
                "The Markov structure ensures tractable inference. By choosing β_t appropriately, "
                "this process can reach arbitrarily small signal-to-noise ratio at t=T, making x_T essentially pure noise. "
                "This enables learning via reverse denoising."
            ),
            citations=[
                "Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. "
                "arXiv:2006.11239.",
                "Song, Y., & Ermon, S. (2019). Generative modeling by estimating gradients of the data distribution. "
                "NeurIPS.",
            ],
            source_line=40,
            concepts=["diffusion", "forward process", "Markov chain", "noise schedule"],
        )

    @staticmethod
    def forward_process_closed_form() -> Equation:
        """Forward process in closed form: directly sample x_t from x_0.

        Express x_t as a function of x_0 and cumulative noise. Enables
        efficient sampling at any time step without iterating.

        Source: diffusion.py:60
        """
        return Equation(
            name="Forward Process (Closed Form)",
            latex=(
                r"x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon, "
                r"\quad \bar{\alpha}_t = \prod_{s=1}^{t} (1 - \beta_s)"
            ),
            description=(
                "Direct sampling: signal term √ᾱ_t x_0 plus noise term √(1-ᾱ_t) ε. "
                "ᾱ_t is the cumulative product of (1-β_s) over all steps."
            ),
            history=(
                "The closed-form solution is key to training efficiency in diffusion models. "
                "Rather than iteratively applying the Markov chain q(x_t|x_{t-1}), "
                "we can sample x_t directly from x_0 in a single step. This closed form reveals the structure: "
                "x_t is a linear combination of signal and noise, with the balance (ᾱ_t) controlled by the schedule β_t. "
                "At t=0: ᾱ_0 ≈ 1, so x_t ≈ x_0 (signal dominates). "
                "At t=T: ᾱ_T ≈ 0, so x_t ≈ ε (noise dominates). "
                "This linearity is crucial for efficient training via noise prediction."
            ),
            citations=[
                "Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. "
                "arXiv:2006.11239.",
            ],
            source_line=60,
            concepts=["forward process", "closed form", "cumulative noise", "direct sampling"],
        )

    @staticmethod
    def reverse_process() -> Equation:
        """Diffusion reverse process: learned denoising to generate samples.

        Reverse the forward process by learning to predict noise and remove it
        at each step, starting from pure noise and recovering data.

        Source: diffusion.py:80
        """
        return Equation(
            name="Diffusion Reverse Process",
            latex=(
                r"p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))"
            ),
            description=(
                "Learned reverse step: predict mean μ_θ and covariance Σ_θ at time t. "
                "Starting from x_T ≈ N(0,I), iteratively denoise: x_T → x_{T-1} → ... → x_0."
            ),
            history=(
                "Reversing the forward process is the core of generation in diffusion models. "
                "If we could learn p(x_{t-1}|x_t) perfectly, sampling x_T ∼ N(0,I) and iterating "
                "would recover samples from the data distribution. However, learning this directly is expensive. "
                "The key insight (Ho et al., 2020): parameterize the reverse process as Gaussian "
                "and learn to predict the noise at each step. This turns the problem into denoising, "
                "which is much more stable and data-efficient than direct density estimation."
            ),
            citations=[
                "Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. "
                "arXiv:2006.11239.",
            ],
            source_line=80,
            concepts=["diffusion", "reverse process", "denoising", "generation"],
        )

    @staticmethod
    def noise_prediction_objective() -> Equation:
        """Diffusion training objective: predict noise in q(x_t|x_0).

        Train a network to predict the Gaussian noise ε added during the forward
        process. This is equivalent to maximum likelihood under certain conditions.

        Source: diffusion.py:100
        """
        return Equation(
            name="Noise Prediction Objective",
            latex=(
                r"\mathcal{L}_{\text{simple}} = \mathbb{E}_{x_0, t, \epsilon} "
                r"[\| \epsilon - \epsilon_\theta(x_t, t) \|_2^2]"
            ),
            description=(
                "Train network ε_θ to predict noise ε sampled from N(0,I). "
                "Minimize L2 distance between predicted and true noise."
            ),
            history=(
                "The simplicity objective is a major practical contribution of diffusion probabilistic models. "
                "Rather than learning the full reverse process distribution or score function, "
                "we train a denoising network to predict the noise added during forward diffusion. "
                "Ho et al. (2020) showed this simple objective is equivalent to maximum likelihood and "
                "more numerically stable than other formulations. The noise prediction formulation enables "
                "training with large batch sizes on standard hardware and has proven remarkably effective. "
                "This simplification was critical to diffusion models' practical success."
            ),
            citations=[
                "Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. "
                "arXiv:2006.11239.",
            ],
            source_line=100,
            concepts=["diffusion", "training objective", "noise prediction", "denoising"],
        )

    @staticmethod
    def score_matching() -> Equation:
        """Score matching: learn the score function (gradient of log probability).

        Train a network s_θ to predict the score ∇_x log p_t(x_t), which
        points toward high-probability regions and enables sampling.

        Source: diffusion.py:120
        """
        return Equation(
            name="Score Matching Objective",
            latex=(
                r"\mathcal{L}_{\text{score}} = \mathbb{E}_{t, x_0, \epsilon} "
                r"\left[ \| s_\theta(x_t, t) + \frac{\epsilon}{\sqrt{1 - \bar{\alpha}_t}} \|_2^2 \right]"
            ),
            description=(
                "Train network s_θ to predict the score ∇log p_t(x_t). "
                "Related to noise prediction by: s_θ(x_t,t) = -ε_θ(x_t,t)/√(1-ᾱ_t)."
            ),
            history=(
                "Score-based generative modeling (Song & Ermon, 2019) provides an alternative viewpoint "
                "to noise-based diffusion. The score function ∇_x log p_t(x_t) points toward high probability "
                "and encodes the direction of steepest ascent in probability. By learning the score, "
                "we can sample via Langevin dynamics or other score-based samplers. "
                "This perspective connects diffusion to classical score-based methods and provides new insights "
                "into convergence and error analysis. Song et al. (2021) showed score-based and noise-based "
                "formulations are equivalent under specific noise schedules."
            ),
            citations=[
                "Song, Y., & Ermon, S. (2019). Generative modeling by estimating gradients of the data distribution. "
                "NeurIPS.",
                "Song, Y., Sohl-Dickstein, J., Kingma, D. P., Kumar, A., Ermon, S., & Poole, B. (2021). "
                "Score-based generative modeling through stochastic differential equations. ICLR.",
            ],
            source_line=120,
            concepts=["score matching", "score function", "gradient of log probability", "Langevin"],
        )

    @staticmethod
    def variance_schedule() -> Equation:
        """Variance schedule β_t: hyperparameter controlling noise at each step.

        Choose schedule β_t to control the diffusion process. Linear, quadratic,
        and learned schedules are used in practice.

        Source: diffusion.py:140
        """
        return Equation(
            name="Variance Schedule",
            latex=(
                r"\beta_t \in \mathbb{R}_{>0}, \quad \text{e.g. } "
                r"\beta_t = \frac{1}{4\sqrt{t}} \text{ or } \beta_t = \frac{s t}{T}"
            ),
            description=(
                "Hyperparameter sequence controlling noise added at each step. "
                "Common choices: linear (s·t/T), quadratic (s·(t/T)²), or cosine schedules."
            ),
            history=(
                "The variance schedule β_t is a key design choice in diffusion models. "
                "It controls the diffusion rate: small β_t means gradual noise addition (many steps needed); "
                "large β_t means rapid diffusion. The schedule affects: (1) number of steps needed to reach noise, "
                "(2) signal-to-noise ratio at each time step, (3) training dynamics. "
                "Ho et al. (2020) used linear schedules; Nichol & Dhariwal (2021) introduced learned schedules. "
                "Recent work shows the schedule affects generation quality significantly. "
                "Different schedules (linear, quadratic, cosine) trade off step count against numerical stability."
            ),
            citations=[
                "Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. "
                "arXiv:2006.11239.",
                "Nichol, A. Q., & Dhariwal, P. (2021). Improved denoising diffusion probabilistic models. ICML.",
            ],
            source_line=140,
            concepts=["variance schedule", "noise schedule", "hyperparameter", "diffusion rate"],
        )

    @staticmethod
    def classifier_free_guidance() -> Equation:
        """Classifier-free guidance: condition generation without training a classifier.

        Use conditional and unconditional score predictions to guide generation
        toward a condition without needing a separate classifier.

        Source: diffusion.py:160
        """
        return Equation(
            name="Classifier-Free Guidance",
            latex=(
                r"\hat{\epsilon}_\theta(x_t, t, c) = \epsilon_\theta(x_t, t, \emptyset) + "
                r"w \left[ \epsilon_\theta(x_t, t, c) - \epsilon_\theta(x_t, t, \emptyset) \right]"
            ),
            description=(
                "Predicted noise: unconditional + w · (conditional - unconditional). "
                "Scale parameter w controls guidance strength (w=0: unconditional, w>>1: strong conditioning)."
            ),
            history=(
                "Classifier-free guidance (Ho & Salimans, 2021) is a powerful technique for conditional "
                "diffusion without training explicit classifiers. The key insight: blend unconditional "
                "and conditional predictions to guide the model. This is related to classifier-based guidance "
                "(Dhariwal & Nichol, 2021) but avoids the need for a separate classifier and its gradients. "
                "By training the model to handle both conditioned and unconditional noise prediction, "
                "we can steer generation at inference time via a single hyperparameter w. "
                "This approach is simpler and has become the standard in many diffusion-based systems."
            ),
            citations=[
                "Ho, S., & Salimans, T. (2021). Classifier-free diffusion guidance. "
                "arXiv:2207.12598.",
                "Dhariwal, P., & Nichol, A. Q. (2021). Diffusion models beat GANs on image synthesis. ICML.",
            ],
            source_line=160,
            concepts=["classifier-free guidance", "conditional generation", "conditioning", "guidance strength"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all diffusion model equations."""
    return {
        "forward_process_markov": DiffusionEquations.forward_process_markov(),
        "forward_process_closed_form": DiffusionEquations.forward_process_closed_form(),
        "reverse_process": DiffusionEquations.reverse_process(),
        "noise_prediction_objective": DiffusionEquations.noise_prediction_objective(),
        "score_matching": DiffusionEquations.score_matching(),
        "variance_schedule": DiffusionEquations.variance_schedule(),
        "classifier_free_guidance": DiffusionEquations.classifier_free_guidance(),
    }
