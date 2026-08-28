# Optional Noumenal adapter

## Why it exists
Utility and agrivoltaic arrays create a GPS-denied under-panel strip that John Deere decks and Optimus are the wrong machines for. Whiplash is a specialized cutter. Thermobrain requests a human when uncertainty is high.

## Rules
1. Not core autonomy.
2. Missions only on paddocks with `kind=agrivoltaic_understory`.
3. Blocked if Ceres-tagged animals are in the polygon (unless owner force-approves HITL).
4. Thermobrain `uncertainty >= 0.45` → HITL.
5. Energy agent may reserve dock kWh; it does not let Noumenal dispatch the microgrid.
6. No public Noumenal API — `NoumenalWhiplashClient` is simulation until credentials exist.

## Swap to live later
Replace methods in `backend/app/integrations/noumenal/whiplash.py` with HTTP calls. Keep the same result dataclass so the planner and HITL do not change.
