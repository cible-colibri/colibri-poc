"""
EmitterProperties class from Emitter interface.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import BoundaryObject, Emitter
from colibri.modules.modules_constants import CP_WATER
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class EmitterProperties(Emitter):
    """Class representing an emitter."""

    def __init__(
        self,
        name: str,
        heat_demands: Dict[str, float] = None,
        radiative_shares: Dict[str, float] = None,
        emitter_properties: Dict[str, Dict[str, Any]] = None,
        operating_modes: Dict[str, str] = None,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        """Initialize a new LayerWallLosses instance."""
        if heat_demands is None:
            heat_demands: Dict[str, float] = dict()
        if radiative_shares is None:
            radiative_shares: Dict[str, float] = dict()
        if emitter_properties is None:
            emitter_properties: Dict[str, Dict[str, Any]] = dict()
        if operating_modes is None:
            operating_modes: Dict[str, str] = dict()
        super().__init__(
            name=name,
            heat_demands=heat_demands,
            radiative_shares=radiative_shares,
            emitter_properties=emitter_properties,
            operating_modes=operating_modes,
        )
        self.project_data = self.define_parameter(
            name="project_data",
            default_value=project_data,
            description="Project data.",
            format=ProjectData,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=[
                Parameter(
                    name="efficiency",
                    default_value=0.8,
                    description="Efficiency of the emitter.",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=True,
                    ),
                ),
                Parameter(
                    name="space_coverage",
                    default_value=1.0,
                    description="Emitter's zone coverage "
                    "(0 = no coverage, 1 = complete coverage).",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=True,
                    ),
                ),
            ],
        )

    def initialize(self) -> bool:
        emitters: List[BoundaryObject] = [
            boundary_object
            for boundary in self.project_data.boundaries
            for boundary_object in boundary.object_collection
            if boundary_object.__class__.__name__ == "Emitter"
        ]
        self.emitter_properties: Dict[str, Dict[str, Any]] = {
            emitter.id: dict() for emitter in emitters
        }
        for emitter in emitters:
            emitter_id: str = emitter.id
            self.emitter_properties[emitter_id]["emitter_type"] = (
                emitter.emitter_type
            )
            self.emitter_properties[emitter_id]["spaces"] = [
                space.id for space in emitter.boundary.spaces
            ]
            self.emitter_properties[emitter_id]["space_coverage"] = (
                emitter.space_coverage
            )
            self.emitter_properties[emitter_id]["radiative_share"] = (
                emitter.radiative_share
            )
            if (emitter.emitter_type == "hydraulic") and (
                emitter.mode == "cooling"
            ):
                self.emitter_properties[emitter_id]["nominal_heating_power"] = (
                    0.0
                )
                self.emitter_properties[emitter_id]["nominal_cooling_power"] = (
                    emitter.nominal_cooling_power
                )
                self.emitter_properties[emitter_id]["temperature_in"] = (
                    emitter.nominal_cooling_supply_temperature
                )
                self.emitter_properties[emitter_id]["temperature_out"] = (
                    emitter.nominal_cooling_supply_temperature
                    + emitter.fluid_nominal_delta_temperature
                )
            if (emitter.emitter_type == "hydraulic") and (
                emitter.mode == "heating"
            ):
                self.emitter_properties[emitter_id]["nominal_cooling_power"] = (
                    0.0
                )
                self.emitter_properties[emitter_id]["nominal_heating_power"] = (
                    emitter.nominal_heating_power
                )
                self.emitter_properties[emitter_id]["temperature_in"] = (
                    emitter.nominal_heating_supply_temperature
                )
                self.emitter_properties[emitter_id]["temperature_out"] = (
                    emitter.nominal_heating_supply_temperature
                    + emitter.fluid_nominal_delta_temperature
                )
            if (emitter.emitter_type == "hydraulic") and (
                emitter.mode == "reversible"
            ):
                self.emitter_properties[emitter_id]["temperature_in"] = (
                    emitter.nominal_heating_supply_temperature
                )
                self.emitter_properties[emitter_id]["temperature_out"] = (
                    emitter.nominal_heating_supply_temperature
                    + emitter.fluid_nominal_delta_temperature
                )
            if emitter.emitter_type == "electric":
                self.emitter_properties[emitter_id]["efficiency"] = (
                    emitter.efficiency
                )
            if emitter.emitter_type == "hydraulic":
                self.emitter_properties[emitter_id]["nominal_flowrate"] = (
                    max(
                        self.emitter_properties[emitter_id][
                            "nominal_cooling_power"
                        ],
                        self.emitter_properties[emitter_id][
                            "nominal_heating_power"
                        ],
                    )
                    / CP_WATER
                    / emitter.fluid_nominal_delta_temperature
                )
                nominal_ua_heating = np.abs(
                    self.emitter_properties[emitter_id]["nominal_heating_power"]
                    / (
                        emitter.nominal_heating_supply_temperature
                        - emitter.default_heating_set_point
                    )
                )
                nominal_ua_cooling = np.abs(
                    self.emitter_properties[emitter_id]["nominal_cooling_power"]
                    / (
                        emitter.default_cooling_set_point
                        - emitter.nominal_cooling_supply_temperature
                    )
                )
                self.emitter_properties[emitter_id]["nominal_ua"] = max(
                    nominal_ua_heating, nominal_ua_cooling
                )
        return True

    def run(self, time_step: int, number_of_iterations: int) -> None:
        print(
            f"[emitter ({time_step}, {number_of_iterations})] {self.heat_demands = }"
        )
        for emitter_id, emitter_properties in self.emitter_properties.items():
            # TODO: Check when there are more than one space for an emitter
            space_id: str = emitter_properties["spaces"][0]
            is_electric: bool = emitter_properties["emitter_type"] == "electric"
            is_hydraulic: bool = (
                emitter_properties["emitter_type"] == "hydraulic"
            )
            is_cooling_mode: bool = self.operating_modes[space_id] == "cooling"
            is_heating_mode: bool = self.operating_modes[space_id] == "heating"
            # Electric emitters
            if is_electric:
                emitter_properties["electric_load"] = (
                    self.heat_demands[space_id]
                    * emitter_properties["space_coverage"]
                    * emitter_properties["efficiency"]
                )
                emitter_properties["phi_radiative"] = (
                    self.heat_demands[space_id]
                    * emitter_properties["space_coverage"]
                    * emitter_properties["radiative_share"]
                )
                emitter_properties["phi_convective"] = (
                    self.heat_demands[space_id]
                    * emitter_properties["space_coverage"]
                    * (1 - emitter_properties["radiative_share"])
                )
                emitter_properties["temperature_out"] = None
            # Hydraulic emitters
            else:
                emitter_properties["electric_load"] = None
                inlet_temperature: float = emitter_properties["temperature_out"]
                if is_hydraulic and is_cooling_mode:
                    inlet_temperature = emitter_properties[
                        "nominal_cooling_supply_temperature"
                    ]
                if is_hydraulic and is_heating_mode:
                    inlet_temperature = emitter_properties[
                        "nominal_heating_supply_temperature"
                    ]
                emitter_properties["temperature_in"] = inlet_temperature
                emitter_properties["phi_radiative"] = (
                    self.heat_demands[space_id]
                    * emitter_properties["space_coverage"]
                    * emitter_properties["radiative_share"]
                )
                emitter_properties["phi_convective"] = (
                    self.heat_demands[emitter_id]
                    * emitter_properties["space_coverage"]
                    * (1 - emitter_properties["radiative_share"])
                )
                emitter_properties["temperature_out"] = (
                    emitter_properties["temperature_in"]
                    - self.heat_demands[space_id]
                    * emitter_properties["space_coverage"]
                    / CP_WATER
                    / self.flow_rates[emitter_id]
                )

    def end_iteration(self, time_step: int) -> None:
        for emitter_id, emitter_properties in self.emitter_properties.items():
            # Electric emitters
            if emitter_properties["emitter_type"] == "electric":
                emitter_properties["previous_electric_load"] = (
                    emitter_properties["electric_load"]
                )
            # Hydraulic emitters
            else:
                emitter_properties["temperature_out"] = emitter_properties[
                    "temperature_out"
                ]

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        threshold: float = 1e-3
        have_emitters_converged: List[bool] = []
        for emitter_id, emitter_properties in self.emitter_properties.items():
            # Electric emitters
            if emitter_properties["emitter_type"] == "electric":
                has_emitter_converged: bool = (
                    abs(
                        emitter_properties["electric_load"]
                        - emitter_properties["previous_electric_load"]
                    )
                    <= threshold
                )
            # Hydraulic emitters
            else:
                has_emitter_converged: bool = (
                    abs(
                        emitter_properties["temperature_out"]
                        - emitter_properties["previous_temperature_out"]
                    )
                    <= threshold
                )
            have_emitters_converged.append(has_emitter_converged)
        self._has_converged = all(has_emitter_converged)
