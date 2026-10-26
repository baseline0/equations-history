"""Equation definitions in SymPy with narrative context."""

# Importing each topic module runs its @equation decorators, which fill the registry.
# The biochemistry and quantum modules fill it from math-trace catalog snapshots instead of decorators.
from . import biochemistry, quantum  # noqa: F401
from .autoencoders import AutoencoderEquations
from .bert import BERTEquations
from .diffusion import DiffusionEquations
from .entropy import EntropyEquations
from .loss_functions import LossFunctionEquations
from .optimizers import OptimizerEquations
from .regularization import RegularizationEquations

__all__ = [
    "AutoencoderEquations",
    "BERTEquations",
    "OptimizerEquations",
    "RegularizationEquations",
    "LossFunctionEquations",
    "DiffusionEquations",
    "EntropyEquations",
]
