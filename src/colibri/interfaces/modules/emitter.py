"""Emitter Interface."""

import abc
from typing import Any, Dict, List

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Emitter(Module, metaclass=abc.ABCMeta):
    """Emitter interface."""

    def __init__(
        self,
        name: str,
        heat_demands: Dict[str, float],
        radiative_shares: Dict[str, float],
        emitter_properties: Dict[str, Dict[str, Any]],
        operating_modes: Dict[str, str],
    ):
        super().__init__(name=name)
        self.heat_demands = self.define_input(
            name="heat_demands",
            default_value=heat_demands,
            description="Heat demand of the spaces - positive=heating, negative=cooling.",
            format=Dict[str, float],
            min=-float("inf"),
            max=float("inf"),
            unit=Units.WATT,
            attached_to=Attachment(
                category=ColibriProjectObjects.SPACE,
                description="Heat demand of the space.",
                format=float,
            ),
        )
        self.radiative_shares = self.define_input(
            name="radiative_shares",
            default_value=radiative_shares,
            description="Radiative shares between Tair and Tmr "
            "for operative temperature control: 0 = Tair, 1 = Tmr.",
            format=Dict[str, float],
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=Attachment(
                category=ColibriProjectObjects.BOUNDARY_OBJECT,
                class_name="Emitter",
            ),
        )
        self.emitter_properties = self.define_output(
            name="emitter_properties",
            default_value=emitter_properties,
            description="Properties of the emitters.",
            format=Dict[str, Dict[str, Any]],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
        )
        self.operating_modes = self.define_input(
            name="operating_modes",
            default_value=operating_modes,
            description="Operating modes (heating, cooling, free_float).",
            format=Dict[str, str],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
        )
