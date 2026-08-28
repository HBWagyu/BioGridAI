from backend.app.services.daily_planner import resolve_approval, run_daily_plan
from backend.app.services.world import new_world


def test_world_boots_tesla_core_and_optional_whiplash():
    w = new_world()
    assert len(w.optimus) == 2
    assert len(w.jd) == 1
    assert len(w.whiplash) == 1
    assert w.whiplash[0].unit_id == "WHIP-01"
    ok, msg = w.chain.verify()
    assert ok, msg


def test_whiplash_blocked_while_animals_in_understory():
    w = new_world()
    under = next(p for p in w.farm.paddocks if p.kind == "agrivoltaic_understory")
    animals = [a for a in w.animals if a.paddock_id == under.paddock_id]
    result = w.noumenal.create_under_array_mission("WHIP-01", under, animals)
    assert result.accepted is False
    assert result.needs_hitl is True
    assert w.whiplash[0].status == "awaiting_teleop"


def test_daily_plan_does_not_create_whiplash_peer_agent():
    w = new_world()
    plan = run_daily_plan(w)
    agents = {t.agent for t in plan.tasks}
    assert "Optimus Fleet" in agents
    assert "Grazing / Carbon" in agents
    assert "Energy / Microgrid" in agents
    assert "Operations Synthesis" in agents
    assert "Whiplash Agent" not in agents
    vendor_tasks = [t for t in plan.tasks if t.vendor == "noumenal"]
    assert vendor_tasks
    assert vendor_tasks[0].assignee.startswith("vendor:whiplash:")


def test_hitl_approve_lowers_understory_height():
    w = new_world()
    run_daily_plan(w)
    under = next(p for p in w.farm.paddocks if p.kind == "agrivoltaic_understory")
    before = under.current_veg_height_in
    therm = next(a for a in w.approvals if a.source == "vendor.noumenal.thermobrain")
    resolve_approval(w, therm.approval_id, "approve")
    assert w.whiplash[0].status == "cutting"
    assert under.current_veg_height_in < before
    ok, _ = w.chain.verify()
    assert ok
