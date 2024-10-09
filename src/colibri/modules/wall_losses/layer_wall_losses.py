"""
LayerWallLosses class from WallLosses interface.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Dict, List, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.wall_losses import WallLosses
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


@unique
class Materials(Enum):
    CONCRETE = "concrete"
    INSULATION = "insulation"
    PLASTER = "plaster"
    WOOD = "wood"


class LayerWallLosses(WallLosses):
    """Class representing a wall losses sing walls' layers."""

    def __init__(
        self,
        name: str,
        inside_air_temperatures: Optional[Dict[str, float]] = None,
        exterior_air_temperature: float = 0.0,
        q_walls: Optional[Dict[str, float]] = None,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        """Initialize a new LayerWallLosses instance."""
        if inside_air_temperatures is None:
            inside_air_temperatures: Dict[str, float] = dict()
        if q_walls is None:
            q_walls: Dict[str, float] = dict()
        super().__init__(
            name=name,
            inside_air_temperatures=inside_air_temperatures,
            exterior_air_temperature=exterior_air_temperature,
            q_walls=q_walls,
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
                    name="thickness",
                    default_value=0.3,
                    description="Thickness of the layer.",
                    format=float,
                    min=0.001,
                    max=2,
                    unit=Units.METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="thermal_conductivity",
                    default_value=1.75,
                    description="Thermal conductivity of the layer.",
                    format=float,
                    min=0.01,
                    max=5,
                    unit=Units.WATT_PER_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="specific_heat",
                    default_value=900,
                    description="Specific heat capacity (known as C) of the layer.",
                    format=float,
                    min=100,
                    max=8_000,
                    unit=Units.JOULE_PER_KILO_GRAM,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="density",
                    default_value=2_500,
                    description="Volumetric density of the layer.",
                    format=float,
                    min=0.1,
                    max=50_000,
                    unit=Units.KILOGRAM_PER_CUBIC_METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="material_type",
                    default_value="concrete",
                    description="Material characterization of the layer.",
                    format=Materials,
                    min=None,
                    max=None,
                    choices=Materials,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
            ],
        )

    def initialize(self) -> None: ...

    def post_initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for boundary in self.project_data.boundaries:
            # TODO: How to handle multiple spaces?
            inside_air_temperature: float = self.inside_air_temperatures.get(
                boundary.spaces[0].label,
                boundary.spaces[0].inside_air_temperature,
            )
            thermal_resistance: float = 0.0
            for layer in boundary.layers:
                thickness: float = layer.thickness
                thermal_conductivity: float = layer.thermal_conductivity
                thermal_resistance += thickness / thermal_conductivity
            thermal_conductance: float = 1.0 / thermal_resistance
            self.q_walls[boundary.label] = (
                thermal_conductance
                * boundary.area
                * (inside_air_temperature - self.exterior_air_temperature)
            )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    data: dict = {
        "name": "layer_wall_losses_1",
        "inside_air_temperatures": {
            "kitchen": 21,
        },
        "exterior_air_temperature": 5.0,
        "boundaries": [
            {
                "name": "boundary-1",
                "module": "GenericBoundary",
                "label": "kitchen-living-room",
                "side_1": "kitchen",
                "side_2": "living-room",
                "area": 4,
                "layers": [
                    {
                        "name": "layer-1",
                        "module": "GenericLayer",
                        "label": "concrete",
                        "thermal_conductivity": 0.5,
                        "specific_heat": 1_050,
                        "density": 2400,
                        "thickness": 0.2,
                    },
                ],
                "spaces": [
                    {
                        "name": "space-1",
                        "module": "GenericSpace",
                        "label": "kitchen",
                        "volume": 120,
                        "reference_area": 40,
                        "inside_air_temperature": 19.5,
                    },
                ],
            }
        ],
    }
    layer_wall_losses: LayerWallLosses = LayerWallLosses.load_from_json(
        data=data
    )
    layer_wall_losses.run(time_step=1, number_of_iterations=1)
    LOGGER.debug(layer_wall_losses.q_walls)
