"""
Building interface.
"""

import abc
from typing import Dict

import numpy as np

from colibri.interfaces.module import Module
from colibri.utils.enums_utils import (
    Units,
)


class Building(Module, metaclass=abc.ABCMeta):
    """Class representing a building (interface)."""

    def __init__(self, name: str, blind_position: float) -> None:
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
        self.flow_rates: float = self.define_output(
            name="flow_rates",
            default_value=0.0,
            description="Flow rates",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.KILOGRAM_PER_SECOND,
            attached_to=None,
        )
        self.heat_fluxes: float = self.define_output(
            name="heat_fluxes",
            default_value=np.array([]),
            description="Heat fluxes",
            format=float,
            min=0,
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
