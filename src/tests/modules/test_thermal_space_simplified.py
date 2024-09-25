"""
Tests for the `thermal_space_simplified.py` module.
"""

from colibri.core import ProjectData
from colibri.interfaces import ThermalSpace
from colibri.modules import ThermalSpaceSimplified
from colibri.project_objects import Space


def test_thermal_space_simplified() -> None:
    """Test the ThermalSpaceSimplified class."""
    space: Space = Space(
        id="space-1",
        label="kitchen",
        volume=120,
        reference_area=40,
        inside_air_temperature=19.5,
        height=2.5,
        setpoint_temperature=26,
        gain=500,
    )
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.spaces = [space]
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal-space-1",
        project_data=project_data,
        previous_inside_air_temperatures={space.label: 26},
        # setpoint_temperatures={space.label: 26},
        # gains={space.label: 500},
    )
    assert isinstance(thermal_space_simplified, ThermalSpaceSimplified) is True
    assert isinstance(thermal_space_simplified, ThermalSpace) is True
    assert thermal_space_simplified.name == "thermal-space-1"
    assert thermal_space_simplified.inside_air_temperatures == dict()
    assert thermal_space_simplified.annual_needs == dict()
    thermal_space_simplified.run(time_step=1, number_of_iterations=1)
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal-space-1",
        setpoint_temperatures={space.label: 26},
        gains={space.label: 300},
    )
    assert thermal_space_simplified.project_data is None


if __name__ == "__main__":
    test_thermal_space_simplified()
