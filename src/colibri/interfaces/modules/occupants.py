"""
Occupants interface (IM_5).
"""

import abc
from typing import Dict

from colibri.interfaces.model import Model
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Occupants(Model, metaclass=abc.ABCMeta):
    """Occupants interface (IM_5)."""

    def __init__(
        self,
        name: str,
        gains: Dict[str, float],
        setpoint_temperatures: Dict[str, float],
    ):
        super().__init__(name=name)
        self.gains = self.define_output(
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
        self.setpoint_temperatures = self.define_output(
            name="setpoint_temperatures",
            default_value=setpoint_temperatures,
            description="Setpoint air temperature for each space.",
            format=Dict[str, float],
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
