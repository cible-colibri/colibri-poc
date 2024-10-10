"""
ThermalBuilding class from Building interface.
"""

from typing import Optional

import numpy as np

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import Building
from colibri.modules.modules_constants import CP_AIR, DENSITY_AIR
from colibri.modules.thermal_spaces.detailed_building.controls import (
    compute_ventilation_losses,
    get_operation_mode,
    space_temperature_control_simple,
)
from colibri.modules.thermal_spaces.detailed_building.rycj import (
    generate_euler_exponential_system_and_control_matrices,
    generate_system_and_control_matrices,
    get_states_from_index,
    run_state_space,
    set_radiative_shares,
    set_u_values,
)
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class ThermalBuilding(Building):
    def __init__(
        self,
        name: str,
        blind_position: float = 1.0,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        super().__init__(name=name, blind_position=blind_position)
        self.name = name
        # TODO: Associate to the project (time_step) instead of module?
        self.time_step = self.define_parameter(
            name="time_step",
            default_value=3_600,
            description="Time step for the simulation.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SECOND,
            attached_to=None,
            required=None,
        )
        self.radiative_share_sensor = self.define_parameter(
            name="radiative_share_sensor",
            default_value=0,
            description="Radiative share between Tair and Tmr "
            "for operative temperature control: 0 = Tair, 1 = Tmr.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.f_sky = self.define_parameter(
            name="f_sky",
            default_value=0.5,
            description="Coefficient to connect the mean radiant temperature "
            "(Tmr) around the building.\n"
            "If f_sky = 0, then Tmr = Tair, "
            "if f_sky = 1, then Tmr = Fsky.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.radiative_share_internal_gains = self.define_parameter(
            name="radiative_share_internal_gains",
            default_value=0.6,
            description="Radiative share for internal gains.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.maximum_number_of_iterations = self.define_parameter(
            name="maximum_number_of_iterations",
            default_value=3,
            description="Maximum number of iteration.",
            format=int,
            min=0,
            max=10_000,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
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
                    name="setpoint_heating",
                    default_value=19.0,
                    description="Heating set-point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="setpoint_cooling",
                    default_value=26.0,
                    description="Cooling set-point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="constant_internal_gains",
                    default_value=26.0,
                    description="Constant internal gains of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="u_value",
                    default_value=0.0,
                    description="Thermal conductance of the boundary.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY,
                        from_archetype=True,
                    ),
                ),
                Parameter(
                    name="u_value",
                    default_value=0.0,
                    description="Thermal conductance of the window.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                Parameter(
                    name="area",
                    default_value=0.0,
                    description="Surface area of the window.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.SQUARE_METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
            ],
        )

    def initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None: ...

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True
