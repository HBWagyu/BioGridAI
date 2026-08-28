"""Optional vendor adapter — NOT core Tesla autonomy.

Whiplash is a specialized under-array vegetation machine.
Thermobrain uncertainty events map onto BioGridAI HITL.
The planner never treats this client as a peer of Optimus.
"""

from .whiplash import NoumenalWhiplashClient

__all__ = ["NoumenalWhiplashClient"]
