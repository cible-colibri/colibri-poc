"""
Tests for the `infinite_power_generator.py` module.
"""

from typing import List

import pytest

from colibri.core import ProjectData
from colibri.interfaces import (
    BoundaryObject,
    Generator,
)
from colibri.modules import (
    InfinitePowerGenerator,
)
from colibri.project_objects import (
    Boundary,
    Space,
)


def test_infinite_power_generator() -> None:
    """Test the InfinitePowerGenerator class."""
    generator: InfinitePowerGenerator = InfinitePowerGenerator(
        name="generator-1",
    )
    assert generator.project_data is None
    space: Space = Space(
        id="space-1",
        label="kitchen",
        volume=120,
        reference_area=40,
        inside_air_temperature=19.5,
        presence_setpoint_temperature=21,
        occupation=[7, 3, 0, 2],
        q_needs=0.0,
    )
    emitter: BoundaryObject = BoundaryObject(
        id="emitter_2",
        label="Emitter kitchen",
        type="emitter",
        type_id="electric_convector",
        x_relative_position=1.0,
        y_relative_position=1.0,
        on_side="side_1",
        z_relative_position=0.0,
        efficiency=0.9,
    )
    boundaries: List[Boundary] = [
        Boundary(
            id="kitchen-living-room",
            label="Kitchen living room",
            side_1="kitchen",
            side_2="living-room",
            area=4,
            azimuth=90,
            tilt=90,
            spaces=[space],
            object_collection=[emitter],
        ),
    ]
    space.boundaries = boundaries
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.spaces = [space]
    generator: InfinitePowerGenerator = InfinitePowerGenerator(
        name="generator-1",
        q_needs={"space-1": 450.0},
        project_data=project_data,
    )
    assert isinstance(generator, InfinitePowerGenerator) is True
    assert isinstance(generator, Generator) is True
    generator.run(time_step=1, number_of_iterations=1)
    assert generator.q_provided["emitter_2"] == pytest.approx(450, abs=1)
    assert generator.q_consumed["emitter_2"] == pytest.approx(500, abs=1)
    assert generator.has_converged(time_step=1, number_of_iterations=1) is True


if __name__ == "__main__":
    test_infinite_power_generator()
