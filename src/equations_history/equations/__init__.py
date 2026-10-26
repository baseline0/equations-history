"""Equation definitions in SymPy with narrative context."""

# Importing each topic module runs its @equation decorators, which fill the registry.
# The biochemistry module fills it from the math-trace catalog snapshot instead of decorators.
from . import biochemistry  # noqa: F401
from .autoencoders import AutoencoderEquations
from .bert import BERTEquations
from .diffusion import DiffusionEquations
from .entropy import EntropyEquations
from .loss_functions import LossFunctionEquations
from .optimizers import OptimizerEquations
from .quantum import QuantumEquations
from .regularization import RegularizationEquations

__all__ = [
    "AutoencoderEquations",
    "BERTEquations",
    "OptimizerEquations",
    "RegularizationEquations",
    "LossFunctionEquations",
    "DiffusionEquations",
    "EntropyEquations",
    "QuantumEquations",
]
