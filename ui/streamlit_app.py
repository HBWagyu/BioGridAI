"""BioGridAI farmer UI — Streamlit. Simulation mode works with no hardware keys."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from backend.app.services.daily_planner import resolve_approval, run_daily_plan
from backend.app.services.world import World, new_world

st.set_page_config(page_title="BioGridAI Tesla Platform", page_icon="🟩", layout="wide")

STATUS_COLOR = {
    "normal": "green",
    "estrus": "orange",
    "calving_watch": "red",
    "processing_queue": "purple",
    "health_flag": "darkred",
}


def get_world() -> World:
    if "world" not in st.session_state:
        st.session_state.world = new_world()
    return st.session_state.world


def farm_map(world: World) -> folium.Map:
    farm = world.farm
    m = folium.Map(location=[farm.lat, farm.lon], zoom_start=15, tiles="OpenStreetMap")
    folium.Polygon(
        farm.parcel_polygon,
        color="#1b4332",
        weight=3,
        fill=True,
        fill_opacity=0.05,
        tooltip=farm.name,
    ).add_to(m)
    if farm.array_polygon:
        folium.Polygon(
            farm.array_polygon,
            color="#f4d35e",
            weight=2,
            fill=True,
            fill_color="#f4d35e",
            fill_opacity=0.25,
            tooltip="Solar array (agrivoltaic understory)",
        ).add_to(m)
    for p in farm.paddocks:
        color = "#40916c" if p.kind != "agrivoltaic_understory" else "#e9c46a"
        folium.Polygon(
            p.polygon,
            color=color,
            weight=2,
            fill=True,
            fill_opacity=0.12,
            tooltip=f"{p.name} · {p.acres} ac · veg {p.current_veg_height_in:.1f} in",
        ).add_to(m)
    for a in world.animals:
        folium.CircleMarker(
            [a.lat, a.lon],
            radius=7,
            color=STATUS_COLOR.get(a.status, "blue"),
            fill=True,
            fill_opacity=0.9,
            tooltip=f"{a.name} [{a.ceres_tag_id}] {a.status}",
        ).add_to(m)
    for r in world.optimus:
        folium.Marker(
            [r.lat, r.lon],
            tooltip=f"Tesla Optimus {r.robot_id} · {r.current_task} · {r.battery_pct:.0f}%",
            icon=folium.Icon(color="red", icon="cog", prefix="fa"),
        ).add_to(m)
    for j in world.jd:
        folium.Marker(
            [j.lat, j.lon],
            tooltip=f"John Deere {j.equipment_id} · {j.current_mission}",
            icon=folium.Icon(color="green", icon="tractor", prefix="fa"),
        ).add_to(m)
    for w in world.whiplash:
        color = "orange" if w.status == "awaiting_teleop" else "gray"
        folium.Marker(
            [w.lat, w.lon],
            tooltip=(
                f"VENDOR Whiplash {w.unit_id} · {w.status} · "
                f"u={w.uncertainty:.2f} · NOT Tesla Optimus"
            ),
            icon=folium.Icon(color=color, icon="leaf", prefix="fa"),
        ).add_to(m)
    return m


def sidebar(world: World) -> str:
    st.sidebar.title("BioGridAI")
    st.sidebar.caption("Tesla-first · farmer-owned · any parcel")
    page = st.sidebar.radio(
        "Navigate",
        [
            "05:30 Briefing",
            "Live Map",
            "Herd / Ceres",
            "Tesla Energy",
            "Optimus Fleet",
            "John Deere",
            "Vendor: Whiplash",
            "HITL Queue",
            "Traceability",
            "Settings",
        ],
    )
    st.sidebar.divider()
    pending = sum(1 for a in world.approvals if a.status == "pending")
    st.sidebar.metric("HITL pending", pending)
    st.sidebar.metric("Head (Ceres)", len(world.animals))
    st.sidebar.metric("Battery SoC", f"{world.energy.battery_soc_pct:.0f}%")
    st.sidebar.caption("Core: Optimus · Opticaster · Ceres Gen 6 · John Deere")
    st.sidebar.caption("Optional vendor: Noumenal Whiplash (under-array only)")
    if st.sidebar.button("Reset simulation"):
        st.session_state.world = new_world()
        st.rerun()
    return page


def page_briefing(world: World) -> None:
    st.title("05:30 Multi-agent briefing")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ceres head", len(world.animals))
    c2.metric("Optimus util", f"{sum(r.util_pct for r in world.optimus)/max(1,len(world.optimus)):.0f}%")
    c3.metric("Solar now", f"{world.energy.solar_kw:.0f} kW")
    c4.metric("SoC", f"{world.energy.battery_soc_pct:.0f}%")
    under = next(p for p in world.farm.paddocks if p.kind == "agrivoltaic_understory")
    c5.metric("Understory veg", f"{under.current_veg_height_in:.1f} in")

    whip = world.whiplash[0] if world.whiplash else None
    st.subheader("Under-array vendor asset (not Tesla core)")
    w1, w2, w3, w4 = st.columns(4)
    if whip and whip.enabled:
        w1.metric("Whiplash", whip.unit_id)
        w2.metric("Status", whip.status)
        w3.metric("Thermobrain u", f"{whip.uncertainty:.2f}")
        w4.metric("Envelope", "agrivoltaic_understory only")
        st.caption(
            "VENDOR · Noumenal Whiplash sits on the array edge as a specialized cutter. "
            "Optimus still owns animal moves. John Deere stays off the drip-edge. "
            "A vegetation pass is emitted by Grazing / Ops Synthesis and always HITL-gated."
        )
    else:
        st.info("Noumenal adapter disabled in Settings. Tesla core (Optimus / Opticaster / Ceres / JD) is unchanged.")

    if st.button("Run multi-agent daily planning", type="primary"):
        plan = run_daily_plan(world)
        st.success(plan.summary)

    if not world.plans:
        st.info("No plan yet. Run planning to generate Tesla-core tasks plus optional vendor vegetation gate.")
        return

    plan = world.plans[0]
    st.subheader(f"Plan {plan.plan_id}")
    st.write(plan.summary)
    df = pd.DataFrame([t.model_dump() for t in plan.tasks])
    st.dataframe(df[["agent", "title", "assignee", "zone", "risk", "requires_hitl", "vendor"]], hide_index=True, use_container_width=True)
    pending = [a for a in world.approvals if a.status == "pending"]
    if pending:
        st.warning(f"{len(pending)} HITL items need the owner — open HITL Queue.")


def page_map(world: World) -> None:
    st.title("Live agrivoltaic map")
    st.caption("Yellow polygon = solar array / Whiplash envelope. Red markers = Tesla Optimus. Gray/orange leaf = optional vendor cutter.")
    st_folium(farm_map(world), width=None, height=560)


def page_herd(world: World) -> None:
    st.title("Herd · Ceres Gen 6")
    df = pd.DataFrame(
        [
            {
                "animal": a.name,
                "tag": a.ceres_tag_id,
                "status": a.status,
                "paddock": a.paddock_id,
                "temp_C": a.temp_c,
                "activity": a.activity,
                "rumination_min": a.rumination_min,
                "tag_battery": a.tag_battery_pct,
            }
            for a in world.animals
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)
    fig = go.Figure()
    fig.add_bar(x=[a.name for a in world.animals], y=[a.temp_c for a in world.animals], name="temp C")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)


def page_energy(world: World) -> None:
    st.title("Tesla Energy / Opticaster")
    e = world.energy
    a, b, c, d = st.columns(4)
    a.metric("Array output", f"{e.solar_kw:.0f} kW")
    b.metric("Site load", f"{e.load_kw:.0f} kW")
    c.metric("Export", f"{e.export_kw:.0f} kW")
    d.metric("Battery", f"{e.battery_soc_pct:.0f}% · {e.battery_kwh:.0f} kWh")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=e.battery_soc_pct,
            title={"text": "Powerwall / Megapack SoC"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#2d6a4f"}},
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "Optional Whiplash dock is a *load*, not a Tesla asset. "
        "Energy agent reserves a charge window; it never hands dispatch to Noumenal."
    )


def page_optimus(world: World) -> None:
    st.title("Tesla Optimus fleet")
    st.dataframe(pd.DataFrame([r.model_dump() for r in world.optimus]), hide_index=True, use_container_width=True)
    st.caption("Core robotics path. Panel clean, patrol, animal move, processing assist — Optimus only.")


def page_jd(world: World) -> None:
    st.title("John Deere field ops")
    st.dataframe(pd.DataFrame([j.model_dump() for j in world.jd]), hide_index=True, use_container_width=True)
    st.caption("Open-field / alley / perimeter only. JD does not enter the under-panel envelope.")


def page_whiplash(world: World) -> None:
    st.title("Optional vendor · Noumenal Whiplash")
    st.warning(
        "This page is a *vendor adapter*, not a sixth core agent. "
        "Whiplash may only cut agrivoltaic understory after animals are cleared by Optimus/JD and HITL."
    )
    for w in world.whiplash:
        st.json(w.model_dump())
    under = next(p for p in world.farm.paddocks if p.kind == "agrivoltaic_understory")
    animals = [a for a in world.animals if a.paddock_id == under.paddock_id]
    st.write(f"Animals still in understory: {', '.join(a.name for a in animals) or 'none'}")
    if st.button("Request simulated under-array mission"):
        result = world.noumenal.create_under_array_mission("WHIP-01", under, animals)
        world.chain.append("vendor.noumenal", "mission_request", str(result))
        st.write(result)
        if result.needs_hitl:
            st.error("Thermobrain / safety gate → HITL Queue")


def page_hitl(world: World) -> None:
    st.title("Human-in-the-loop queue")
    pending = [a for a in world.approvals if a.status == "pending"]
    if not pending:
        st.success("No pending approvals.")
    for appr in reversed(world.approvals):
        with st.expander(f"{appr.status.upper()} · {appr.title} · {appr.source}", expanded=appr.status == "pending"):
            st.write(appr.recommendation)
            st.caption(appr.impact)
            if appr.status == "pending":
                c1, c2, c3 = st.columns(3)
                if c1.button("Approve", key=f"ok-{appr.approval_id}"):
                    resolve_approval(world, appr.approval_id, "approve")
                    st.rerun()
                comment = c2.text_input("Override reason", key=f"c-{appr.approval_id}")
                if c2.button("Override", key=f"no-{appr.approval_id}"):
                    resolve_approval(world, appr.approval_id, "override", comment)
                    st.rerun()
                if c3.button("Request video", key=f"vid-{appr.approval_id}"):
                    resolve_approval(world, appr.approval_id, "video")
                    st.rerun()


def page_trace(world: World) -> None:
    st.title("Traceability · hash chain")
    ok, msg = world.chain.verify()
    st.write(msg if ok else f"CHAIN BROKEN: {msg}")
    rows = [
        {
            "seq": e.seq,
            "time": e.timestamp.isoformat(),
            "actor": e.actor,
            "type": e.event_type,
            "details": e.details,
            "hash": e.hash[:16] + "…",
        }
        for e in world.chain.events
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def page_settings(world: World) -> None:
    st.title("Settings · farm profile")
    farm = world.farm
    st.write(
        {
            "name": farm.name,
            "address": farm.address,
            "acres": farm.acres,
            "solar_kwp": farm.solar_kwp,
            "battery_kwh": farm.battery_kwh,
            "species": farm.species,
            "carbon": farm.target_carbon_program,
        }
    )
    st.info(
        "Replace this generic demo parcel with your GeoJSON / drawn boundary. "
        "No live site coordinates are hard-coded. Simulation mode needs no API keys."
    )
    world.whiplash[0].enabled = st.toggle("Enable optional Noumenal Whiplash adapter", value=world.whiplash[0].enabled)


def main() -> None:
    world = get_world()
    page = sidebar(world)
    {
        "05:30 Briefing": page_briefing,
        "Live Map": page_map,
        "Herd / Ceres": page_herd,
        "Tesla Energy": page_energy,
        "Optimus Fleet": page_optimus,
        "John Deere": page_jd,
        "Vendor: Whiplash": page_whiplash,
        "HITL Queue": page_hitl,
        "Traceability": page_trace,
        "Settings": page_settings,
    }[page](world)


if __name__ == "__main__":
    main()
