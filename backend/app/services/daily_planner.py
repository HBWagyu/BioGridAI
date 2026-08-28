"""Five Tesla-core agents + optional vendor vegetation task from Grazing/Ops.

Whiplash is scheduled by Grazing + Operations Synthesis.
There is no sixth peer 'Whiplash agent'.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from backend.app.models.domain import Approval, DailyPlan, PlanTask
from backend.app.services.world import World


def _tid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:6]}"


def run_daily_plan(world: World) -> DailyPlan:
    farm = world.farm
    energy = world.energy
    under = next(p for p in farm.paddocks if p.kind == "agrivoltaic_understory")
    recovery = next(p for p in farm.paddocks if p.paddock_id == "P3")
    animals_under = [a for a in world.animals if a.paddock_id == under.paddock_id]
    calving = [a for a in world.animals if a.status == "calving_watch"]
    health = [a for a in world.animals if a.status == "health_flag"]
    estrus = [a for a in world.animals if a.status == "estrus"]

    tasks: list[PlanTask] = []
    approvals: list[Approval] = []

    tasks.append(
        PlanTask(
            task_id=_tid("OPT"),
            agent="Optimus Fleet",
            title="Thermal / visual patrol of calving-watch animals",
            assignee="optimus:OPT-01",
            zone=",".join(a.paddock_id for a in calving) or "P2",
            risk="medium",
            requires_hitl=True,
            energy_kwh=2.4,
            notes="Optimus confirms Ceres calving-watch with onboard vision. HITL if assist likely.",
        )
    )
    tasks.append(
        PlanTask(
            task_id=_tid("OPT"),
            agent="Optimus Fleet",
            title="Move understory herd to East Recovery before any cut",
            assignee="optimus:OPT-02",
            zone=f"{under.paddock_id}->{recovery.paddock_id}",
            risk="medium",
            requires_hitl=True,
            energy_kwh=3.1,
            notes="Required before optional Whiplash under-array mission. Tesla robot owns the animal move.",
        )
    )
    world.optimus_client.assign_task("OPT-01", "calving_visual_confirm", under.paddock_id)

    shade_carbon = round(under.shade_hours_yesterday * len(animals_under) * 0.12, 2)
    tasks.append(
        PlanTask(
            task_id=_tid("GRZ"),
            agent="Grazing / Carbon",
            title=f"Rotate {len(animals_under)} head off array understory (veg {under.current_veg_height_in:.1f} in)",
            assignee="human",
            zone=under.paddock_id,
            risk="medium",
            requires_hitl=True,
            notes=(
                f"Forage index {under.forage_index:.2f}. Shade-carbon proxy +{shade_carbon} "
                "VM0042-style units (model only). Cut only after animals clear."
            ),
        )
    )

    whip = world.whiplash[0] if world.whiplash else None
    if whip and whip.enabled:
        result = world.noumenal.create_under_array_mission(
            whip.unit_id, under, animals_under, force=False
        )
        tasks.append(
            PlanTask(
                task_id=_tid("VEG"),
                agent="Operations Synthesis",
                title="Optional under-array vegetation pass (Noumenal Whiplash adapter)",
                assignee=f"vendor:whiplash:{whip.unit_id}",
                zone=under.paddock_id,
                risk="high" if result.needs_hitl else "medium",
                requires_hitl=True,
                energy_kwh=4.8,
                vendor="noumenal",
                notes=(
                    "NOT core Tesla autonomy. Restricted to agrivoltaic_understory. "
                    + (result.blocked_reason or result.teleop_reason or "Ready after animal-clear + HITL.")
                ),
            )
        )
        if result.needs_hitl:
            approvals.append(
                Approval(
                    approval_id=_tid("HITL"),
                    created_at=datetime.now(timezone.utc),
                    risk="high",
                    title="Thermobrain / animal-clearance gate for Whiplash",
                    recommendation=result.teleop_reason or result.blocked_reason or "Review under-array cut",
                    impact="Prevents cutter/animal interaction; logs teleop minutes into hash chain.",
                    source="vendor.noumenal.thermobrain",
                )
            )

    if health:
        tasks.append(
            PlanTask(
                task_id=_tid("HLT"),
                agent="Herd Health",
                title=f"Ceres health flag: {health[0].name} ({health[0].ceres_tag_id})",
                assignee="optimus:OPT-01",
                zone=health[0].paddock_id,
                risk="high",
                requires_hitl=True,
                notes=f"Temp {health[0].temp_c} C, activity {health[0].activity}. Optimus visual + owner call.",
            )
        )
    if estrus:
        tasks.append(
            PlanTask(
                task_id=_tid("BRD"),
                agent="Herd Health",
                title=f"Estrus: review pairing for {estrus[0].name}",
                assignee="human",
                zone=estrus[0].paddock_id,
                risk="medium",
                requires_hitl=True,
                notes="Breeding recommendation requires owner approval per HITL mandate.",
            )
        )

    reserve = 18.0 if whip and whip.enabled else 12.0
    note = world.energy_client.reserve_charge_window(reserve)
    tasks.append(
        PlanTask(
            task_id=_tid("NRG"),
            agent="Energy / Microgrid",
            title="Hold export through late-morning robot + optional dock window",
            assignee="tesla:opticaster",
            zone="site",
            risk="low",
            energy_kwh=reserve,
            notes=(
                f"Solar {energy.solar_kw:.0f} kW, SoC {energy.battery_soc_pct:.0f}%, "
                f"export {energy.export_kw:.0f} kW. {note}. "
                "Do not schedule under-array cut during forecast peak unless shading loss exceeds export."
            ),
        )
    )

    tasks.append(
        PlanTask(
            task_id=_tid("JD"),
            agent="Operations Synthesis",
            title="JD alley / perimeter mow (open geometry only)",
            assignee="jd:JD-8R-01",
            zone="P1,P3",
            risk="low",
            energy_kwh=8.0,
            notes="John Deere stays out of under-panel envelope. Whiplash (if used) owns drip-edge.",
        )
    )
    world.jd_client.create_mission("JD-8R-01", "perimeter_mow", "P1")

    approvals.append(
        Approval(
            approval_id=_tid("HITL"),
            created_at=datetime.now(timezone.utc),
            risk="medium",
            title="Approve understory herd move P2 → P3",
            recommendation="Move 6 head off array so vegetation pass can run later today.",
            impact="+recovery on P2, shade-carbon paused during move, enables optional vendor cut.",
            source="grazing",
        )
    )

    plan = DailyPlan(
        plan_id=_tid("PLAN"),
        created_at=datetime.now(timezone.utc),
        summary=(
            f"{len(tasks)} tasks · {len(approvals)} HITL items · "
            f"array veg {under.current_veg_height_in:.1f} in over target · "
            f"Whiplash adapter={'on' if whip and whip.enabled else 'off'}"
        ),
        tasks=tasks,
        kpis={
            "headcount": len(world.animals),
            "optimus_units": len(world.optimus),
            "pending_hitl": len(approvals),
            "solar_kw": energy.solar_kw,
            "battery_soc_pct": energy.battery_soc_pct,
            "understory_veg_in": under.current_veg_height_in,
            "shade_carbon_proxy": shade_carbon,
        },
    )
    world.plans.insert(0, plan)
    world.approvals.extend(approvals)
    world.chain.append("planner", "daily_plan", f"{plan.plan_id}: {plan.summary}")
    return plan


def resolve_approval(world: World, approval_id: str, action: str, comment: str = "") -> Approval:
    appr = next(a for a in world.approvals if a.approval_id == approval_id)
    if action == "approve":
        appr.status = "approved"
        if appr.source == "vendor.noumenal.thermobrain" and world.whiplash:
            world.noumenal.resolve_teleop(world.whiplash[0].unit_id, True, comment)
            under = next(p for p in world.farm.paddocks if p.kind == "agrivoltaic_understory")
            under.current_veg_height_in = max(under.target_veg_height_in, under.current_veg_height_in - 4.0)
    elif action == "override":
        appr.status = "overridden"
        appr.comment = comment
        if appr.source == "vendor.noumenal.thermobrain" and world.whiplash:
            world.noumenal.resolve_teleop(world.whiplash[0].unit_id, False, comment)
    elif action == "video":
        appr.status = "video_requested"
    world.chain.append("owner", f"hitl_{appr.status}", f"{appr.approval_id} {appr.title} {comment}")
    return appr
