"""
Weather interface (IM_4).
"""

import abc

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Weather(Module, metaclass=abc.ABCMeta):
    """Weather interface (IM_4)."""

    def __init__(
        self,
        name: str,
        exterior_air_temperature: float,
    ):
        super().__init__(name=name)
        self.exterior_air_temperature = self.define_output(
            name="exterior_air_temperature",
            default_value=exterior_air_temperature,
            description="Exterior air temperature.",
            format=float,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
