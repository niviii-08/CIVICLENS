"""
Backend database models initialization.
Imports all models to ensure SQLAlchemy mapper relationships register cleanly.
"""
from backend.models import (
    common, budget, manifesto, promise, news, funding,
    representative, claim, civic_issue, graph, entity_registry,
    policy_evaluation, accountability, procurement, cag_rti, provenance
)

__all__ = [
    "common", "budget", "manifesto", "promise", "news", "funding",
    "representative", "claim", "civic_issue", "graph", "entity_registry",
    "policy_evaluation", "accountability", "procurement", "cag_rti", "provenance"
]

