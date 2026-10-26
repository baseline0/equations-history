"""Quantum computing equations: qubit states, the Bloch sphere, measurement, gates, Grover's search, Shor's order finding,
and the quantum Fourier transform.

Unlike the other topic modules, these formulas are not written here. They come from math-trace's quantum_formulas module,
through the snapshot in catalogs/ and its manifest, which records the math-trace commit it was copied from. Each formula's
residual is checked in math-trace, where the emitter refuses to write a formula that fails. The narrative (names, history,
citations, concepts) is in narratives/. Refresh with `just sync-catalog quantum catalogs/quantum_formulas.json`.
"""

from equations_history.constants import CATALOG_DIR, NARRATIVE_DIR
from equations_history.core import Equation
from equations_history.formula_catalog import register_catalog_topic
from equations_history.registry import equations_for

TOPIC = "quantum"
# Where the formulas are defined in math-trace. Each recorded source_line points into this file.
MATH_TRACE_MODEL = "src/math_trace/quantum_formulas.py"

register_catalog_topic(
    topic=TOPIC,
    module=__name__,
    catalog_path=CATALOG_DIR / f"{TOPIC}.json",
    narrative_path=NARRATIVE_DIR / f"{TOPIC}.json",
    source_file=MATH_TRACE_MODEL,
)


def get_all_equations() -> dict[str, Equation]:
    """Return all quantum computing equations."""
    return equations_for(TOPIC)
