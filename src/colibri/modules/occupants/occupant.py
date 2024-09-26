"""
OccupantModel class from Occupant interface.
"""

from __future__ import annotations

from typing import Dict, Optional

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
        occupant_per_square_meter: float = 1.0 / 40,
        occupant_gains: float = 100,
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
                    name="occupant_gains",
                    default_value=occupant_gains,
                    description="Gain generated by a single occupant.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=None,
                    required=None,
                ),
                Parameter(
                    name="occupant_per_square_meter",
                    default_value=occupant_per_square_meter,
                    description="Number of occupants per square meter.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
            ],
        )

    def initialize(self) -> None: ...

    def post_initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            self.gains[space.label] = (
                space.occupation[time_step]
                * space.occupant_per_square_meter
                * space.reference_area
                * space.occupant_gains
            )
            if space.occupation[time_step] > 0:
                self.setpoint_temperatures[space.label] = (
                    space.presence_setpoint_temperature
                )
            else:
                self.setpoint_temperatures[space.label] = (
                    space.absence_setpoint_temperature
                )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...
