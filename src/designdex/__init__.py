"""A searchable UI/UX design knowledge base, ranked with BM25.

The corpus is 1,429 rows spread over ten domains (styles, colour palettes,
font pairings, chart selection, UX guidelines, ...) and thirteen technology
stacks. The tables are redistributed from the MIT-licensed ui-ux-pro-max-skill;
see LICENSE-DATA. Everything is plain CSV, so the whole thing is auditable
with a text editor and there is nothing to keep in sync with a database.

Typical use::

    from designdex import search, generate_design_system

    search("dark analytics dashboard")
    print(generate_design_system("fintech mobile app", "Ledger"))

The command line interface is a thin wrapper over the same functions.
"""

from .core import (
    AVAILABLE_STACKS,
    BM25,
    CSV_CONFIG,
    MAX_RESULTS,
    STACK_CONFIG,
    detect_domain,
    search,
    search_stack,
)
from .design_system import generate_design_system, persist_design_system

__all__ = [
    "AVAILABLE_STACKS",
    "CSV_CONFIG",
    "MAX_RESULTS",
    "STACK_CONFIG",
    "BM25",
    "detect_domain",
    "search",
    "search_stack",
    "generate_design_system",
    "persist_design_system",
]

__version__ = "0.1.0"
