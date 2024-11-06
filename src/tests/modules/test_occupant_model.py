"""
Tests for the `occupant.py` module.
"""

import pytest

from colibri.core import ProjectData
from colibri.interfaces import Occupants
from colibri.modules import OccupantModel
from colibri.project_objects import Space


def test_occupant_model() -> None:
    """Test the GenericWindow class."""
    space: Space = Space(
        id="space-1",
        label="kitchen",
        volume=120,
        reference_area=40,
        inside_air_temperature=19.5,
        presence_setpoint_temperature=21,
        absence_setpoint_temperature=16,
        occupation=[7, 3, 0, 2],
        q_needs=0.0,
        occupant_per_square_meter=1.0 / 40,
        occupant_gains=100,
    )
    project_data: ProjectData = ProjectData("project-data-1", data=dict())
    project_data.spaces = [space]
    occupant: OccupantModel = OccupantModel(name="occupant-1")
    assert occupant.project_data is None
    occupant: OccupantModel = OccupantModel(
        name="occupant-1", gains={"space-1": 700}, project_data=project_data
    )
    assert isinstance(occupant, OccupantModel) is True
    assert isinstance(occupant, Occupants) is True
    assert occupant.gains == {"space-1": 700}
    assert occupant.setpoint_temperatures == dict()
    occupant.run(time_step=1, number_of_iterations=2)
    assert occupant.gains["space-1"] == pytest.approx(300, abs=1)
    assert occupant.setpoint_temperatures == {"space-1": 21}
    occupant.run(time_step=2, number_of_iterations=2)
    assert occupant.gains["space-1"] == pytest.approx(0, abs=1)
    assert occupant.setpoint_temperatures == {"space-1": 16}
    assert occupant.has_converged(time_step=1, number_of_iterations=2) is True


if __name__ == "__main__":
    test_occupant_model()
