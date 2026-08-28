"""John Deere Operations Center client. Exclusive field-equipment path."""

from __future__ import annotations

from backend.app.models.domain import JDAsset


class JohnDeereClient:
    def __init__(self, fleet: list[JDAsset], simulation: bool = True) -> None:
        self.fleet = fleet
        self.simulation = simulation

    def list_equipment(self) -> list[JDAsset]:
        return self.fleet

    def create_mission(self, equipment_id: str, mission: str, zone: str) -> JDAsset:
        unit = next(u for u in self.fleet if u.equipment_id == equipment_id)
        unit.current_mission = f"{mission}@{zone}"
        unit.status = "autonomous_mission"
        return unit
