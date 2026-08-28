"""Optional Noumenal Whiplash + Thermobrain adapter (SIMULATION).

This is NOT core Tesla autonomy.
- Optimus remains the only general robot the planner owns.
- John Deere remains the only field-equipment path.
- Whiplash may only receive vegetation.under_array missions inside the solar array polygon.
- Thermobrain uncertainty is converted into BioGridAI HITL approvals.

No public Noumenal API exists yet. Live control stays simulated.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.models.domain import Animal, Paddock, WhiplashAsset


UNCERTAINTY_HITL_THRESHOLD = 0.45


@dataclass
class WhiplashMissionResult:
    unit_id: str
    accepted: bool
    status: str
    uncertainty: float
    teleop_reason: str | None
    needs_hitl: bool
    blocked_reason: str | None = None


class NoumenalWhiplashClient:
    def __init__(self, units: list[WhiplashAsset], simulation: bool = True) -> None:
        self.units = units
        self.simulation = simulation

    def list_units(self) -> list[WhiplashAsset]:
        return self.units

    def _unit(self, unit_id: str) -> WhiplashAsset:
        return next(u for u in self.units if u.unit_id == unit_id)

    def create_under_array_mission(
        self,
        unit_id: str,
        zone: Paddock,
        animals_in_zone: list[Animal],
        force: bool = False,
    ) -> WhiplashMissionResult:
        unit = self._unit(unit_id)
        if not unit.enabled:
            return WhiplashMissionResult(
                unit_id=unit_id,
                accepted=False,
                status=unit.status,
                uncertainty=unit.uncertainty,
                teleop_reason=None,
                needs_hitl=False,
                blocked_reason="Whiplash adapter disabled",
            )
        if zone.kind != "agrivoltaic_understory":
            return WhiplashMissionResult(
                unit_id=unit_id,
                accepted=False,
                status=unit.status,
                uncertainty=unit.uncertainty,
                teleop_reason=None,
                needs_hitl=False,
                blocked_reason="Whiplash is restricted to agrivoltaic understory zones",
            )
        live_animals = [a for a in animals_in_zone if a.status != "processing_queue"]
        if live_animals and not force:
            unit.status = "awaiting_teleop"
            unit.teleop_reason = (
                f"{len(live_animals)} Ceres-tagged animals still in {zone.paddock_id}. "
                "Move with Optimus/JD first."
            )
            unit.uncertainty = 0.82
            return WhiplashMissionResult(
                unit_id=unit_id,
                accepted=False,
                status=unit.status,
                uncertainty=unit.uncertainty,
                teleop_reason=unit.teleop_reason,
                needs_hitl=True,
                blocked_reason=unit.teleop_reason,
            )

        height_gap = max(0.0, zone.current_veg_height_in - zone.target_veg_height_in)
        unit.uncertainty = min(0.95, 0.16 + height_gap * 0.04)
        unit.current_row = f"{zone.paddock_id}-row-sim"
        unit.last_cut_height_in = zone.current_veg_height_in
        if unit.uncertainty >= UNCERTAINTY_HITL_THRESHOLD and not force:
            unit.status = "awaiting_teleop"
            unit.teleop_reason = (
                f"Thermobrain uncertainty {unit.uncertainty:.2f} "
                f"(veg {zone.current_veg_height_in:.1f} in vs target {zone.target_veg_height_in:.1f} in). "
                "Possible drip-edge obstacle / GPS-denied row."
            )
            return WhiplashMissionResult(
                unit_id=unit_id,
                accepted=False,
                status=unit.status,
                uncertainty=unit.uncertainty,
                teleop_reason=unit.teleop_reason,
                needs_hitl=True,
            )

        unit.status = "cutting"
        unit.teleop_reason = None
        return WhiplashMissionResult(
            unit_id=unit_id,
            accepted=True,
            status=unit.status,
            uncertainty=unit.uncertainty,
            teleop_reason=None,
            needs_hitl=False,
        )

    def resolve_teleop(self, unit_id: str, approved: bool, comment: str = "") -> WhiplashAsset:
        unit = self._unit(unit_id)
        if approved:
            unit.status = "cutting"
            unit.uncertainty = 0.20
            unit.teleop_reason = None
        else:
            unit.status = "idle"
            unit.teleop_reason = comment or "owner override — mission cancelled"
        return unit
