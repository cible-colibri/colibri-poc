"""
Generator interface (IM_2).
"""

import abc
from typing import Dict

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Generator(Module, metaclass=abc.ABCMeta):
    """Generator interface (IM_2)."""

    def __init__(
        self,
        name: str,
        q_needs: Dict[str, float],
        q_provided: Dict[str, float],
        q_consumed: Dict[str, float],
    ):
        super().__init__(name=name)
        self.q_needs = self.define_input(
            name="q_needs",
            default_value=q_needs,
            description="Spaces' needs.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
                description="Needs of the space.",
                default_value=0.0,
                format=float,
            ),
        )
        self.q_provided = self.define_output(
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
                description="Power provided by the emitter.",
                format=float,
            ),
        )
        self.q_consumed = self.define_output(
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
                description="Power consumed by the emitter.",
                format=float,
            ),
        )
