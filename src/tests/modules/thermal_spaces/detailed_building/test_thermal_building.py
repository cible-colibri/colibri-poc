"""
Tests for the `thermal_building.py` module.
"""

from pathlib import Path

import pytest

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.interfaces import Building
from colibri.modules import (
    AirFlowBuilding,
    ThermalBuilding,
    WeatherEpw,
)


def test_thermal_building() -> None:
    """Test the thermal_building class."""
    # Create a building (from SimpleBuilding model) and add it to the project orchestrator
    multi_zone_building: ThermalBuilding = ThermalBuilding(
        name="building-1", blind_position=1
    )
    assert isinstance(multi_zone_building, ThermalBuilding) is True
    assert isinstance(multi_zone_building, Building) is True
    assert multi_zone_building.name == "building-1"
    assert (
        multi_zone_building.has_converged(time_step=1, number_of_iterations=1)
        is True
    )


@pytest.mark.xfail(reason="in progress...")
def test_thermal_building_case_1() -> None:
    """Test the thermal_building class in a case."""
    # Create a project orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-1",
        time_steps=8_760,
        iterate_for_convergence=True,
        maximum_number_of_iterations=100,
    )
    # Create a weather (from Weather model) and add it to the project orchestrator
    epw_file_path: Path = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "weather"
        / "epw"
        / "Paris.epw"
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-1",
        epw_file_path=epw_file_path,
        constant_ground_temperature=10.0,
    )
    project_orchestrator.add_model(model=weather)
    # Create project data
    project_file: Path = (
        Path(__file__).resolve().parents[3] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    project_orchestrator.add_model(project_data)
    # Create a building (from SimpleBuilding model) and add it to the project orchestrator
    multi_zone_building: ThermalBuilding = ThermalBuilding(
        name="building-1", blind_position=1
    )
    project_orchestrator.add_model(model=multi_zone_building)
    # Add air flow model
    air_flow_building: AirFlowBuilding = AirFlowBuilding(name="air-flow-1")
    project_orchestrator.add_model(air_flow_building)
    # Link modules
    project_orchestrator.add_link(
        weather, "sky_temperatures", air_flow_building, "sky_temperatures"
    )
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperatures",
        air_flow_building,
        "exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        air_flow_building, "flow_rates", multi_zone_building, "flow_rates"
    )
    project_orchestrator.add_link(
        multi_zone_building,
        "space_temperatures",
        air_flow_building,
        "space_temperatures",
    )
    # Run project_orchestrator
    project_orchestrator.run()


if __name__ == "__main__":
    test_thermal_building()
    test_thermal_building_case_1()
