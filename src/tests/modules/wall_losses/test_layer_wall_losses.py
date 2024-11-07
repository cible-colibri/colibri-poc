"""
Tests for the `layer_wall_losses.py` module.
"""

from typing import List

import pytest

from colibri.core import ProjectData
from colibri.interfaces import (
    ElementObject,
    WallLosses,
)
from colibri.modules import (
    LayerWallLosses,
)
from colibri.project_objects import (
    Boundary,
    Space,
)


def test_layer_wall_losses() -> None:
    """Test the LayerWallLosses class."""
    space: Space = Space(
        id="space-1",
        label="kitchen",
        volume=120,
        reference_area=40,
        inside_air_temperature=19.5,
    )
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-1",
            "label": "concrete",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.2,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-2",
            "label": "concrete",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.4,
        },
    )
    boundary_1: Boundary = Boundary(
        id="boundary-1",
        label="kitchen-living-room",
        side_1="space-1",
        side_2="living-room",
        area=4,
        azimuth=90,
        tilt=90,
        layers=[layer_1],
        spaces=[space],
    )
    boundary_2: Boundary = Boundary(
        id="boundary-2",
        label="kitchen-restroom",
        side_1="space-1",
        side_2="restroom",
        area=2.5,
        azimuth=90,
        tilt=90,
        layers=[layer_1, layer_2],
        spaces=[space],
    )
    boundaries: List[Boundary] = [
        boundary_1,
        boundary_2,
    ]
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.spaces = [space]
    project_data.boundaries = boundaries
    wall_losses: LayerWallLosses = LayerWallLosses(
        name="wall-losses-1",
        project_data=project_data,
    )
    assert isinstance(wall_losses, LayerWallLosses) is True
    assert isinstance(wall_losses, WallLosses) is True
    assert wall_losses.name == "wall-losses-1"
    for time_step in range(0, 3):
        wall_losses.run(time_step=time_step, number_of_iterations=1)
        assert wall_losses.q_walls["boundary-1"] == pytest.approx(195, abs=1)
        assert wall_losses.q_walls["boundary-2"] == pytest.approx(40, abs=1)
        assert (
            wall_losses.has_converged(
                time_step=time_step, number_of_iterations=1
            )
            is True
        )
    wall_losses_2: LayerWallLosses = LayerWallLosses(
        name="wall-losses-2",
    )
    assert wall_losses_2.project_data is None


if __name__ == "__main__":
    test_layer_wall_losses()
