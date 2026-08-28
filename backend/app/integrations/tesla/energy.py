"""Tesla Energy / Opticaster client stub."""

from __future__ import annotations

from backend.app.models.domain import EnergySnapshot


class TeslaEnergyClient:
    def __init__(self, snapshot: EnergySnapshot, simulation: bool = True) -> None:
        self.snapshot = snapshot
        self.simulation = simulation

    def now(self) -> EnergySnapshot:
        return self.snapshot

    def reserve_charge_window(self, kwh: float) -> str:
        # Tesla synergy: agrivoltaic load (robots + processing + optional vendor dock) planned against SoC.
        return f"Reserved {kwh:.1f} kWh buffer on Powerwall/Megapack (sim)"

    # TODO: Replace stub with official Tesla Energy / Opticaster endpoints when available.
