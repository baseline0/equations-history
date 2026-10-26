"""Biochemistry equations: Michaelis-Menten enzyme kinetics.

Unlike the other topic modules, these formulas are not written here. They come from math-trace's biochemistry template,
through the snapshot in catalogs/ and its manifest, which records the math-trace commit it was copied from. The narrative
(names, history, citations, concepts) is in narratives/. Refresh the snapshot with `just sync-catalog biochemistry`.
"""

from equations_history.constants import CATALOG_DIR, NARRATIVE_DIR
from equations_history.core import Equation
from equations_history.formula_catalog import register_catalog_topic
from equations_history.registry import equations_for

TOPIC = "biochemistry"
# Where the formulas are defined in math-trace. Each recorded source_line points into this file.
MATH_TRACE_MODEL = "templates/biochemistry/src/model.py"

register_catalog_topic(
    topic=TOPIC,
    module=__name__,
    catalog_path=CATALOG_DIR / f"{TOPIC}.json",
    narrative_path=NARRATIVE_DIR / f"{TOPIC}.json",
    source_file=MATH_TRACE_MODEL,
)


def get_all_equations() -> dict[str, Equation]:
    """Return all biochemistry equations."""
    return equations_for(TOPIC)
