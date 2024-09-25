"""Acv interface (IM_6)."""

import abc
from typing import Dict

from colibri.interfaces.model import Model
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Acv(Model, metaclass=abc.ABCMeta):
    """Acv interface (IM_6)."""

    def __init__(
        self,
        name: str,
        q_consumed: Dict[str, float],
        co2_impact: float,
    ):
        super().__init__(name=name)
        self.q_consumed = self.define_input(
            name="q_consumed",
            default_value=q_consumed,
            description="Power consumed by all the emitters.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.BOUNDARY_OBJECT,
                class_name="Emitter",
            ),
        )
        self.co2_impact = self.define_output(
            name="co2_impact",
            default_value=co2_impact,
            description="Kilogram equivalent of CO2.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.CO2_KILO_GRAM_EQUIVALENT,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
