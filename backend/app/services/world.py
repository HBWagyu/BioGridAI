"""In-memory world used by Streamlit and FastAPI simulation mode."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.integrations.ceres import CeresGen6Client
from backend.app.integrations.johndeere import JohnDeereClient
from backend.app.integrations.noumenal import NoumenalWhiplashClient
from backend.app.integrations.tesla import OptimusFleetClient, TeslaEnergyClient
from backend.app.models.domain import Approval, DailyPlan
from backend.app.utils.hash_chain import HashChain
from backend.app.utils.simulation_data import clone_state


@dataclass
class World:
    farm: object
    animals: list
    optimus: list
    jd: list
    whiplash: list
    energy: object
    approvals: list[Approval] = field(default_factory=list)
    plans: list[DailyPlan] = field(default_factory=list)
    chain: HashChain = field(default_factory=HashChain)
    simulation: bool = True

    @property
    def optimus_client(self) -> OptimusFleetClient:
        return OptimusFleetClient(self.optimus, self.simulation)

    @property
    def energy_client(self) -> TeslaEnergyClient:
        return TeslaEnergyClient(self.energy, self.simulation)

    @property
    def ceres(self) -> CeresGen6Client:
        return CeresGen6Client(self.animals, self.simulation)

    @property
    def jd_client(self) -> JohnDeereClient:
        return JohnDeereClient(self.jd, self.simulation)

    @property
    def noumenal(self) -> NoumenalWhiplashClient:
        return NoumenalWhiplashClient(self.whiplash, self.simulation)


def new_world() -> World:
    raw = clone_state()
    world = World(
        farm=raw["farm"],
        animals=raw["animals"],
        optimus=raw["optimus"],
        jd=raw["jd"],
        whiplash=raw["whiplash"],
        energy=raw["energy"],
    )
    world.chain.append("system", "boot", "Simulation world initialized (Tesla-pure core + optional Noumenal adapter)")
    return world
