from __future__ import annotations

from ninja import Router

from apps.simulation.schemas import SimulationIn, SimulationOut
from apps.simulation.services import calculate_simulation

simulation_router = Router(tags=["simulation"])


@simulation_router.post("/calculate", response=SimulationOut, auth=None)
def calculate(request, payload: SimulationIn):  # noqa: ANN001, ANN201
    return calculate_simulation(
        goal=payload.goal,
        contribution=payload.contribution,
        frequency=payload.frequency,
        years=payload.years,
        avg_return=payload.avg_return,
    )
