"""
Air flow interface.
"""

import abc
from typing import Any, Dict, List

from numpy import ndarray
from pandas import Series

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class AirFlow(Module, metaclass=abc.ABCMeta):
    """Air flow interface."""

    def __init__(
        self,
        name: str,
        space_temperatures: Dict[str, ndarray],
        sky_temperatures: Series,
        exterior_air_temperatures: Series,
        pressures: Dict[str, ndarray],
        flow_rates: List[List[Any]],
    ):
        """Initialize a new  AirFlow instance."""
        super().__init__(name=name)
        self.space_temperatures = self.define_input(
            name="space_temperatures",
            default_value=space_temperatures,
            description="Temperatures of the space.",
            format=Dict[str, ndarray],
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.sky_temperatures = self.define_input(
            name="sky_temperatures",
            default_value=sky_temperatures,
            description="Sky temperatures.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
            use_post_initialization=True,
        )
        self.exterior_air_temperatures = self.define_input(
            name="exterior_air_temperatures",
            default_value=exterior_air_temperatures,
            description="Exterior air temperatures.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
            use_post_initialization=True,
        )
        self.pressures = self.define_output(
            name="pressures",
            default_value=pressures,
            description="Pressures of the spaces.",
            format=ndarray,
            min=0,
            max=float("inf"),
            unit=Units.PASCAL,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
        self.flow_rates = self.define_output(
            name="flow_rates",
            default_value=flow_rates,
            description="Flow rates of the spaces.",
            format=List[List[Any]],
            min=0,
            max=float("inf"),
            unit=Units.KILOGRAM_PER_SECOND,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
