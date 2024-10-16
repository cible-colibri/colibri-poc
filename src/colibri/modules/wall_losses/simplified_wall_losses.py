"""
SimplifiedWallLosses class from WallLosses interface.
"""

from __future__ import annotations

from typing import Dict, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.wall_losses import WallLosses
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class SimplifiedWallLosses(WallLosses):
    def __init__(
        self,
        name: str,
        inside_air_temperatures: Optional[Dict[str, float]] = None,
        exterior_air_temperature: float = 0.0,
        q_walls: Optional[Dict[str, float]] = None,
        project_data: Optional[ProjectData] = None,
    ):
        if inside_air_temperatures is None:
            inside_air_temperatures: Dict[str, float] = dict()
        if q_walls is None:
            q_walls: Dict[str, float] = dict()
        super().__init__(
            name=name,
            inside_air_temperatures=inside_air_temperatures,
            exterior_air_temperature=exterior_air_temperature,
            q_walls=q_walls,
        )
        self.project_data = self.define_parameter(
            name="project_data",
            default_value=project_data,
            description="Project data.",
            format=ProjectData,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=[
                Parameter(
                    name="u_value",
                    default_value=None,
                    description="Thermal conductance.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY,
                        from_archetype=True,
                    ),
                ),
            ],
        )

    def initialize(self) -> bool: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for boundary in self.project_data.boundaries:
            # TODO: How to handle multiple spaces?
            inside_air_temperature: float = self.inside_air_temperatures.get(
                boundary.spaces[0].label,
                boundary.spaces[0].inside_air_temperature,
            )
            self.q_walls[boundary.label] = (
                boundary.u_value
                * boundary.area
                * (inside_air_temperature - self.exterior_air_temperature)
            )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True
