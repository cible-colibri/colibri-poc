"""
WallLosses interface (IM_1).
"""

import abc
from typing import Dict

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class WallLosses(Module, metaclass=abc.ABCMeta):
    """WallLosses interface (IM_1)."""

    def __init__(
        self,
        name: str,
        inside_air_temperatures: Dict[str, float],
        exterior_air_temperature: float,
        q_walls: Dict[str, float],
    ):
        super().__init__(name=name)
        self.inside_air_temperatures = self.define_input(
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
        self.exterior_air_temperature = self.define_input(
            name="exterior_air_temperature",
            default_value=exterior_air_temperature,
            description="Outside air temperature.",
            format=float,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
        self.q_walls = self.define_output(
            name="q_walls",
            default_value=q_walls,
            description="Losses through all the boundaries.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.BOUNDARY,
                description="Losses through the boundary.",
                format=float,
            ),
        )
