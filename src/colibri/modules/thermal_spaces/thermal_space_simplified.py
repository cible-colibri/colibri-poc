"""
ThermalSpaceSimplified class from ThermalSpace interface.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.thermal_space import ThermalSpace
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class ThermalSpaceSimplified(ThermalSpace):
    """Class representing a thermal space for energy balance."""

    def __init__(
        self,
        name: str,
        q_walls: Optional[Dict[str, float]] = None,
        setpoint_temperatures: Optional[Dict[str, float]] = None,
        q_provided: Optional[Dict[str, float]] = None,
        gains: Optional[Dict[str, float]] = None,
        previous_inside_air_temperatures: Optional[Dict[str, float]] = None,
        inside_air_temperatures: Optional[Dict[str, float]] = None,
        q_needs: Optional[Dict[str, float]] = None,
        annual_needs: Optional[Dict[str, float]] = None,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        """Initialize a new ThermalSpaceSimplified instance."""
        if q_walls is None:
            q_walls: Dict[str, float] = dict()
        if setpoint_temperatures is None:
            setpoint_temperatures: Dict[str, float] = dict()
        if q_provided is None:
            q_provided: Dict[str, float] = dict()
        if gains is None:
            gains: Dict[str, float] = dict()
        if previous_inside_air_temperatures is None:
            previous_inside_air_temperatures: Dict[str, float] = dict()
        if inside_air_temperatures is None:
            inside_air_temperatures: Dict[str, float] = dict()
        if q_needs is None:
            q_needs: Dict[str, float] = dict()
        if annual_needs is None:
            annual_needs: Dict[str, float] = dict()
        super().__init__(
            name=name,
            q_walls=q_walls,
            setpoint_temperatures=setpoint_temperatures,
            q_provided=q_provided,
            gains=gains,
            previous_inside_air_temperatures=previous_inside_air_temperatures,
            inside_air_temperatures=inside_air_temperatures,
            q_needs=q_needs,
            annual_needs=annual_needs,
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
                    name="height",
                    default_value=2.5,
                    description="Height of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                        from_archetype=False,
                    ),
                ),
                Parameter(
                    name="layers",
                    default_value=[],
                    description="Layers of a boundary.",
                    format=List["Layer"],
                    min=None,
                    max=None,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ARCHETYPE,
                        class_name="Boundary",
                        from_element_object="Layer",
                    ),
                ),
                Parameter(
                    name="emissivity",
                    default_value=0.92,
                    description="Emissivity of the layer, compared to the reference of a perfect black body.",
                    format=float,
                    min=0,
                    max=1,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="light_reflectance",
                    default_value=0.8,
                    description="Light reflectance (also known as LRV) of the "
                    "layer when used as a boundary's surface."
                    "Measure of solar light (visible + non "
                    "visible light) that is reflected from a "
                    "surface when illuminated by a light source.",
                    format=float,
                    min=0.05,
                    max=1,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="albedo",
                    default_value=0.25,
                    description="Albedo of the layer, which is the light "
                    "reflectance (also known as LRV) of the layer "
                    "when used as a boundary's surface. Measure of "
                    "solar light (visible + non visible light) "
                    "that is reflected from a surface when "
                    "illuminated by a light source.",
                    format=float,
                    min=0,
                    max=1,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="setpoint_temperature",
                    default_value=19,
                    description="Setpoint temperature.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                        from_archetype=False,
                    ),
                ),
                Parameter(
                    name="reference_area",
                    default_value=50,
                    description="Reference area of the space's surface",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.SQUARE_METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                        from_archetype=False,
                    ),
                ),
                Parameter(
                    name="gain",
                    default_value=0,
                    description="gain",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                        from_archetype=False,
                    ),
                ),
            ],
        )
        self.thermal_capacity = 1_230.0  # J/(m³.K)
        self.previous_setpoint_temperature = 20.0  # °C
        self.temporary_annual_needs = dict()

    def initialize(self) -> bool:
        self.previous_setpoint_temperature = 20.0
        self.temporary_annual_needs = {
            space.id: 0.0 for space in self.project_data.spaces
        }
        return True

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            q_walls: float = sum(
                [
                    self.q_walls.get(boundary.id, 0.0)
                    for boundary in space.boundaries
                ]
            )
            self.q_needs[space.id] = (
                (
                    self.setpoint_temperatures.get(
                        space.id,
                        space.setpoint_temperature,
                    )
                    - self.previous_inside_air_temperatures.get(
                        space.id,
                        space.inside_air_temperature,
                    )
                )
                * self.thermal_capacity
                * space.reference_area
                * space.height
                + q_walls
                - self.gains.get(
                    space.id,
                    space.gain,
                )
            )
            emitters = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.type == "emitter"
            ]
            q_provided: float = sum(
                # TODO: Use id instead of label
                [
                    self.q_provided.get(emitter.label, 0.0)
                    for emitter in emitters
                ]
            )
            q_effective: float = (
                q_provided + self.gains.get(space.id, space.gain) - q_walls
            )
            self.inside_air_temperatures[space.id] = (
                self.previous_inside_air_temperatures.get(
                    space.id,
                    space.inside_air_temperature,
                )
                + q_effective
                / (self.thermal_capacity * space.reference_area * space.height)
            )
            self.temporary_annual_needs[space.id] += (
                (
                    self.setpoint_temperatures.get(
                        space.id,
                        space.setpoint_temperature,
                    )
                    - self.previous_setpoint_temperature
                )
                * (self.thermal_capacity * space.reference_area * space.height)
                + q_walls
                - self.gains.get(
                    space.id,
                    space.gain,
                )
            ) / space.reference_area

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None:
        for space in self.project_data.spaces:
            self.annual_needs[space.id] = self.temporary_annual_needs[space.id]

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True
