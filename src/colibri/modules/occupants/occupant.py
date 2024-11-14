"""
OccupantModel class from Occupant interface.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.occupants import Occupants
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class OccupantModel(Occupants):
    def __init__(
        self,
        name: str,
        gains: Optional[Dict[str, float]] = None,
        setpoint_temperatures: Optional[Dict[str, float]] = None,
        project_data: Optional[ProjectData] = None,
    ):
        if gains is None:
            gains: Dict[str, float] = dict()
        if setpoint_temperatures is None:
            setpoint_temperatures: Dict[str, float] = dict()
        super().__init__(
            name=name, gains=gains, setpoint_temperatures=setpoint_temperatures
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
                    name="occupation",
                    default_value=[],
                    description="space occupation for each timestep",
                    format=List["float"],
                    min=0,
                    max=float("inf"),
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="presence_setpoint_temperature",
                    default_value=19,
                    description="setpoint temperature when space is occupied",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="absence_setpoint_temperature",
                    default_value=19,
                    description="setpoint temperature when space is unoccupied",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
            ],
        )
        # TODO: Use define_field maybe with no role?
        self.occupant_per_square_meter = 1.0 / 40.0
        self.occupant_gains = 100.0  # W

    def initialize(self) -> bool: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            self.gains[space.id] = (
                space.occupation[time_step]
                * self.occupant_per_square_meter
                * space.reference_area
                * self.occupant_gains
            )

            if space.occupation[time_step] > 0:
                self.setpoint_temperatures[space.id] = (
                    space.presence_setpoint_temperature
                )
            else:
                self.setpoint_temperatures[space.id] = (
                    space.absence_setpoint_temperature
                )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True
