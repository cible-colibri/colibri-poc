"""
ThermalSpace interface (IM_3).
"""

import abc
from typing import Dict

from colibri.interfaces.model import Model
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class ThermalSpace(Model, metaclass=abc.ABCMeta):
    """ThermalSpace interface (IM_4)."""

    def __init__(
        self,
        name: str,
        q_walls: Dict[str, float] = dict(),
        setpoint_temperatures: Dict[str, float] = dict(),
        q_provided: Dict[str, float] = dict(),
        gains: Dict[str, float] = dict(),
        previous_inside_air_temperatures: Dict[str, float] = dict(),
        inside_air_temperatures: Dict[str, float] = dict(),
        q_needs: Dict[str, float] = dict(),
        annual_needs: Dict[str, float] = dict(),
    ):
        super().__init__(name=name)
        self.q_walls = self.define_input(
            name="q_walls",
            default_value=q_walls,
            description="Losses through all the boundaries.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.BOUNDARY,
            ),
        )
        self.setpoint_temperatures = self.define_input(
            name="setpoint_temperatures",
            default_value=setpoint_temperatures,
            description="Setpoint air temperature for each space.",
            format=float,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.q_provided = self.define_input(
            name="q_provided",
            default_value=q_provided,
            description="Power provided by all the emitters.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.BOUNDARY_OBJECT,
                class_name="Emitter",
            ),
        )
        self.gains = self.define_input(
            name="gains",
            default_value=gains,
            description="Occupation gains for each space.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.previous_inside_air_temperatures = self.define_input(
            name="previous_inside_air_temperatures",
            default_value=previous_inside_air_temperatures,
            description="Inside air temperature of the spaces "
            "at the previous time step.",
            format=Dict[str, float],
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.inside_air_temperatures = self.define_output(
            name="inside_air_temperatures",
            default_value=inside_air_temperatures,
            description="Inside air temperature of the spaces.",
            format=Dict[str, float],
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.q_needs = self.define_output(
            name="q_needs",
            default_value=q_needs,
            description="Spaces' needs.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.annual_needs = self.define_output(
            name="annual_needs",
            default_value=annual_needs,
            description="Annual needs.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
