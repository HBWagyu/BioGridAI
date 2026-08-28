"""BioGridAI Tesla Platform — FastAPI. Simulation-first."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.services.daily_planner import resolve_approval, run_daily_plan
from backend.app.services.world import World, new_world

app = FastAPI(
    title="BioGridAI Tesla Platform API",
    description=(
        "Universal Tesla-first agrivoltaics OS. "
        "Core: Optimus + Opticaster + Ceres Gen 6 + John Deere. "
        "Optional vendor: Noumenal Whiplash under-array adapter (sim)."
    ),
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORLD: World = new_world()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "simulation": WORLD.simulation,
        "core": ["tesla.optimus", "tesla.energy", "ceres.gen6", "johndeere"],
        "optional_vendor": ["noumenal.whiplash"],
    }


@app.get("/farm")
def farm():
    return WORLD.farm.model_dump()


@app.get("/state")
def state():
    return {
        "farm": WORLD.farm.model_dump(),
        "animals": [a.model_dump() for a in WORLD.animals],
        "optimus": [o.model_dump() for o in WORLD.optimus],
        "jd": [j.model_dump() for j in WORLD.jd],
        "whiplash": [w.model_dump() for w in WORLD.whiplash],
        "energy": WORLD.energy.model_dump(),
        "approvals_pending": sum(1 for a in WORLD.approvals if a.status == "pending"),
    }


@app.post("/plan/run")
def plan_run():
    plan = run_daily_plan(WORLD)
    return plan.model_dump()


@app.post("/approvals/{approval_id}/{action}")
def approval_action(approval_id: str, action: str, comment: str = ""):
    return resolve_approval(WORLD, approval_id, action, comment).model_dump()
