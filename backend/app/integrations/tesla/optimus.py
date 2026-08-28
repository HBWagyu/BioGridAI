"""Tesla Optimus fleet client. Stub until official fleet control plane exists."""

from __future__ import annotations

from backend.app.models.domain import OptimusRobot


class OptimusFleetClient:
    """Core robotics path. All general robot work goes through Optimus."""

    def __init__(self, units: list[OptimusRobot], simulation: bool = True) -> None:
        self.units = units
        self.simulation = simulation

    def list_units(self) -> list[OptimusRobot]:
        return self.units

    def assign_task(self, robot_id: str, task: str, zone: str) -> OptimusRobot:
        unit = next(u for u in self.units if u.robot_id == robot_id)
        unit.current_task = f"{task}@{zone}"
        unit.status = "tasking"
        unit.util_pct = min(95.0, unit.util_pct + 12)
        return unit

    # TODO: Replace stub with real Tesla Optimus Fleet SDK when released.
