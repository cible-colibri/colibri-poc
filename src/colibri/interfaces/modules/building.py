"""
Building interface.
"""

import abc
from typing import Any, Dict, List

import numpy as np
from pandas import Series

from colibri.interfaces.module import Module
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class Building(Module, metaclass=abc.ABCMeta):
    """Class representing a building (interface)."""

    def __init__(
        self,
        name: str,
        blind_position: float,
        sky_temperatures: Series,
        exterior_air_temperatures: Series,
        rolling_exterior_air_temperatures: Series,
        direct_radiations: Series,
        diffuse_radiations: Series,
        ground_temperatures: Series,
        flow_rates: List[List[Any]],
        heat_fluxes: Dict[str, float],
        emitter_properties: Dict[str, Dict[str, Any]],
        operating_modes: Dict[str, str],
    ) -> None:
        """Initialize a new Building instance."""
        super().__init__(name=name)
        self.blind_position = self.define_input(
            name="blind_position",
            default_value=blind_position,
            description="Position of the blinds (0=close, 1=open).",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
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
        )
        self.rolling_exterior_air_temperatures: Series = self.define_output(
            name="rolling_exterior_air_temperatures",
            default_value=rolling_exterior_air_temperatures,
            description="Exterior rolling air temperatures.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.direct_radiations = self.define_input(
            name="direct_radiations",
            default_value=direct_radiations,
            description="Direct radiations.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
        self.diffuse_radiations = self.define_input(
            name="diffuse_radiations",
            default_value=diffuse_radiations,
            description="Diffuse radiations.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
        self.ground_temperatures: Series = self.define_input(
            name="ground_temperatures",
            default_value=ground_temperatures,
            description="Temperatures of the ground.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.flow_rates = self.define_input(
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
        self.emitters_radiative_gains = self.define_input(
            name="emitters_radiative_gains",
            default_value=np.array([]),
            description="Radiative gains (phi) from emitters.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=None,
        )
        self.emitter_properties = self.define_input(
            name="emitter_properties",
            default_value=emitter_properties,
            description="Properties of the emitters.",
            format=Dict[str, Dict[str, Any]],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
        )

        self.emitters_convective_gains = self.define_input(
            name="emitters_convective_gains",
            default_value=np.array([]),
            description="Convective gains (phi) from emitters.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=None,
        )
        self.emitters_latent_gains = self.define_input(
            name="emitters_latent_gains",
            default_value=np.array([]),
            description="Latent gains (phi) from emitters.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT,
            attached_to=None,
        )
        self.flow_rates = self.define_output(
            name="flow_rates",
            default_value=0.0,
            description="Flow rates",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.KILOGRAM_PER_SECOND,
            attached_to=None,
        )
        self.heat_fluxes = self.define_output(
            name="heat_fluxes",
            default_value=heat_fluxes,
            description="Heat fluxes",
            format=Dict[str, float],
            min=-float("inf"),
            max=float("inf"),
            unit=Units.WATT,
            attached_to=None,
        )
        self.space_temperatures = self.define_output(
            name="space_temperatures",
            default_value=dict(),
            description="Temperatures of the space.",
            format=Dict[str, float],
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.operating_modes = self.define_output(
            name="operating_modes",
            default_value=operating_modes,
            description="Operating modes (heating, cooling, free_float).",
            format=Dict[str, str],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
        )
