"""
CircularEconomyIndicator class from CircularEconomy interface.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import CircularEconomy
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class CircularEconomyIndicator(CircularEconomy):
    """Class representing a ACV exploitation."""

    CIRCULARITY_SCORES: Dict[str, float] = {
        "re-usable": 1.0,
        "recyclable": 0.7,
        "non-reusable": 0.0,
    }

    def __init__(
        self,
        name: str,
        circularity_score: float = 0.0,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        """Initialize a new CircularEconomyIndicatorinstance."""

        super().__init__(
            name=name,
            circularity_score=circularity_score,
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
                    name="constitutive_materials",
                    default_value=[{"share": 1, "material_type": "concrete"}],
                    description="Collection of materials composing the layer, "
                    "described by a list of dictionnaries having "
                    "'share' (ratio) and "
                    "'constitutive_material_type' (enum)."
                    "The sum of the share of each element of the "
                    "collection as to be equal to 1.",
                    format=List[Dict[str, Any]],
                    min=None,
                    max=None,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        from_archetype=True,
                        class_name="Layer",
                    ),
                ),
                Parameter(
                    name="end_of_life_properties",
                    default_value=None,
                    description="Possible use of the layer at the end of its "
                    "life (recyclability, waste, etc.) by share of "
                    "the layer material.\n"
                    "For example:\n"
                    "[{'share':0.3, 'end_of_life_properties':'re-usable'},"
                    "{'share':0.7, 'end_of_life_properties':'non-reusable'}].\n"
                    "The sum of the share of each element of the "
                    "collection as to be equal to 1.",
                    format=List[Dict[str, Any]],
                    min=None,
                    max=None,
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

    def run(self, time_step: int, number_of_iterations: int) -> None: ...

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None:
        self.circularity_score: float = 0
        for boundary in self.project_data.boundaries:
            for layer in boundary.layers:
                for material, end_of_life_property in zip(
                    layer.constitutive_materials, layer.end_of_life_properties
                ):
                    self.circularity_score += (
                        material["share"]
                        * self.CIRCULARITY_SCORES[
                            end_of_life_property["end_of_life_properties"]
                        ]
                    )


if __name__ == "__main__":
    from colibri.interfaces import ElementObject
    from colibri.project_objects import Boundary

    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-1",
            "label": "concrete",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.2,
            "constitutive_materials": [
                {"share": 1, "material_type": "concrete"},
            ],
            "end_of_life_properties": [
                {"share": 1, "end_of_life_properties": "non-reusable"}
            ],
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-2",
            "label": "wood",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.4,
            "constitutive_materials": [
                {"share": 1, "material_type": "wood"},
            ],
            "end_of_life_properties": [
                {"share": 1, "end_of_life_properties": "recyclable"}
            ],
        },
    )
    boundaries: List[Boundary] = [
        Boundary(
            id="boundary-1",
            label="kitchen-living-room",
            side_1="kitchen",
            side_2="living-room",
            area=4,
            azimuth=90,
            tilt=90,
            layers=[layer_1],
        ),
        Boundary(
            id="boundary-2",
            label="kitchen-restroom",
            side_1="kitchen",
            side_2="restroom",
            area=2.5,
            azimuth=90,
            tilt=90,
            layers=[layer_1, layer_2],
        ),
    ]
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.boundaries = boundaries
    circular_economy_indicator: CircularEconomyIndicator = (
        CircularEconomyIndicator(
            name="circular-economy",
            project_data=project_data,
        )
    )
    assert isinstance(circular_economy_indicator, CircularEconomyIndicator)
    assert isinstance(circular_economy_indicator, CircularEconomy)
    circular_economy_indicator.end_simulation()
    assert circular_economy_indicator.circularity_score == 0.7
