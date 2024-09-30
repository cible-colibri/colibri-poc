"""
Air flow interface.
"""

import abc
from typing import Dict

from numpy import ndarray

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
        pressures: Dict[str, ndarray],
        flow_rates: Dict[str, ndarray],
    ):
        """Initialize a new  AirFlow instance."""
        super().__init__(name=name)
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
            format=ndarray,
            min=0,
            max=float("inf"),
            unit=Units.KILOGRAM_PER_SECOND,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
            ),
        )
