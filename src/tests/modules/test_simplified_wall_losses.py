"""
Tests for the `simplified_wall_losses.py` module.
"""

from typing import List

import pytest

from colibri.core import ProjectData
from colibri.interfaces import WallLosses
from colibri.modules import SimplifiedWallLosses
from colibri.project_objects import Boundary, Space


def test_simplified_wall_losses() -> None:
    """Test the SimplifiedWallLosses class."""
    space: Space = Space(
        id="space-1",
        label="kitchen",
        volume=120,
        reference_area=40,
        inside_air_temperature=19.5,
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
            spaces=[space],
            u_value=0.8,
        ),
        Boundary(
            id="boundary-2",
            label="kitchen-restroom",
            side_1="kitchen",
            side_2="restroom",
            area=2.5,
            azimuth=90,
            tilt=90,
            spaces=[space],
            u_value=0.8,
        ),
    ]
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.spaces = [space]
    project_data.boundaries = boundaries
    wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="wall-losses-1",
        project_data=project_data,
    )
    assert isinstance(wall_losses, SimplifiedWallLosses) is True
    assert isinstance(wall_losses, WallLosses) is True
    assert wall_losses.name == "wall-losses-1"
    for time_step in range(0, 3):
        wall_losses.run(time_step=time_step, number_of_iterations=1)
        assert wall_losses.q_walls["kitchen-living-room"] == pytest.approx(
            62, abs=1
        )
        assert wall_losses.q_walls["kitchen-restroom"] == pytest.approx(
            39, abs=1
        )
    wall_losses_2: SimplifiedWallLosses = SimplifiedWallLosses(
        name="wall-losses-2",
    )
    assert wall_losses_2.project_data is None


if __name__ == "__main__":
    test_simplified_wall_losses()
