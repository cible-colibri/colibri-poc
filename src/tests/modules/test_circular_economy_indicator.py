"""
Tests for the `circularity_economy_indicator.py` module.
"""

from typing import List

from colibri.core import ProjectData
from colibri.interfaces import CircularEconomy, ElementObject
from colibri.modules import CircularEconomyIndicator
from colibri.project_objects import Boundary


def test_circular_economy_indicator() -> None:
    """Test the CircularEconomyIndicator class."""

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
    assert (
        circular_economy_indicator.has_converged(
            time_step=1, number_of_iterations=1
        )
        is True
    )


if __name__ == "__main__":
    test_circular_economy_indicator()
