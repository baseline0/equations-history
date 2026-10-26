"""Shared Equation record used by every equations-history topic module.

Callers never pass ``source``. It is captured from the frame that constructed
the record, so it names the ``Equation(`` call site and needs no maintenance
when code moves.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import FrameType

# Frames from this file (__post_init__) and from the dataclass-generated
# __init__ (compiled from "<string>") are skipped when locating the caller.
_INTERNAL_FILENAMES = frozenset({__file__, "<string>"})


@dataclass
class Equation:
    """One equation with its narrative metadata and code location.

    ``id`` is stable and unique across the package, in the form
    ``"<module>.<name>"`` (for example ``"autoencoders.deterministic_encoder"``).
    ``name`` is the display name.
    """

    id: str
    name: str
    latex: str
    description: str
    history: str
    citations: list[str]
    concepts: list[str]
    source: tuple[str, int] = field(init=False)

    def __post_init__(self) -> None:
        """Record (filename, lineno) of the code that constructed this equation."""
        frame: FrameType | None = sys._getframe(1)
        while frame is not None and frame.f_code.co_filename in _INTERNAL_FILENAMES:
            frame = frame.f_back
        if frame is None:
            self.source = ("<unknown>", 0)
        else:
            self.source = (frame.f_code.co_filename, frame.f_lineno)

    @property
    def source_label(self) -> str:
        """Location for display, such as ``"autoencoders.py:42"``.

        A source is an absolute path when this package's code defines the equation. A catalog equation's source is a
        relative path into math-trace, such as ``"templates/biochemistry/src/model.py:32"``, and is shown in full, so
        it cannot be mistaken for a file in this repo.
        """
        filename, lineno = self.source
        if not Path(filename).is_absolute():
            return f"{filename}:{lineno}"
        return f"{Path(filename).name}:{lineno}"
