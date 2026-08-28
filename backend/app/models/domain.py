"""Pydantic domain models. Location-agnostic farm profile."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    lat: float
    lon: float


class Paddock(BaseModel):
    paddock_id: str
    name: str
    kind: Literal["open_pasture", "agrivoltaic_understory", "holding", "exclusion"] = "open_pasture"
    polygon: list[tuple[float, float]]
    acres: float
    forage_index: float = 0.7
    occupancy_head: int = 0
    target_veg_height_in: float = 8.0
    current_veg_height_in: float = 6.0
    shade_hours_yesterday: float = 0.0


class Animal(BaseModel):
    animal_id: str
    ceres_tag_id: str
    name: str
    sex: Literal["F", "M"]
    status: Literal["normal", "estrus", "calving_watch", "processing_queue", "health_flag"] = "normal"
    lat: float
    lon: float
    activity: float = 70.0
    rumination_min: float = 420.0
    temp_c: float = 38.6
    tag_battery_pct: float = 88.0
    paddock_id: str


class OptimusRobot(BaseModel):
    robot_id: str
    status: Literal["idle", "tasking", "charging", "fault"] = "idle"
    battery_pct: float = 82.0
    lat: float
    lon: float
    current_task: str = "standby"
    util_pct: float = 0.0


class JDAsset(BaseModel):
    equipment_id: str
    name: str
    kind: str = "tractor"
    status: Literal["idle", "autonomous_mission", "manual", "fault"] = "idle"
    lat: float
    lon: float
    current_mission: str = "none"


class WhiplashAsset(BaseModel):
    """Optional vendor asset. Not a Tesla Optimus unit."""

    unit_id: str
    status: Literal["idle", "cutting", "awaiting_teleop", "docked", "fault"] = "docked"
    battery_pct: float = 91.0
    lat: float
    lon: float
    uncertainty: float = 0.12
    current_row: str = "none"
    last_cut_height_in: float | None = None
    teleop_reason: str | None = None
    enabled: bool = True


class EnergySnapshot(BaseModel):
    solar_kw: float
    load_kw: float
    battery_soc_pct: float
    battery_kwh: float
    export_kw: float
    import_kw: float
    forecast_peak_kw: float


class PlanTask(BaseModel):
    task_id: str
    agent: str
    title: str
    assignee: str
    zone: str
    risk: Literal["low", "medium", "high"] = "low"
    requires_hitl: bool = False
    energy_kwh: float = 0.0
    notes: str = ""
    vendor: str | None = None


class Approval(BaseModel):
    approval_id: str
    created_at: datetime
    risk: Literal["medium", "high"]
    title: str
    recommendation: str
    impact: str
    status: Literal["pending", "approved", "overridden", "video_requested"] = "pending"
    source: str
    comment: str = ""


class EventRecord(BaseModel):
    seq: int
    timestamp: datetime
    actor: str
    event_type: str
    details: str
    prev_hash: str
    payload_sha256: str
    hash: str


class FarmProfile(BaseModel):
    name: str
    address: str
    lat: float
    lon: float
    acres: float
    timezone: str = "America/Chicago"
    solar_kwp: float = 250.0
    battery_kwh: float = 270.0
    species: str = "cattle"
    target_carbon_program: str = "Verra VM0042 ready (data model only)"
    parcel_polygon: list[tuple[float, float]]
    array_polygon: list[tuple[float, float]] = Field(default_factory=list)
    paddocks: list[Paddock] = Field(default_factory=list)
    notes: str = "Universal demo profile. Replace geometry with your parcel."


class DailyPlan(BaseModel):
    plan_id: str
    created_at: datetime
    summary: str
    tasks: list[PlanTask]
    kpis: dict[str, float | int | str] = Field(default_factory=dict)
    hash: str = ""
