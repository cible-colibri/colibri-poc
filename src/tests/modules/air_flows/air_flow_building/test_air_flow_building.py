"""
Tests for the `air_flow_building.py` module.
"""

from pathlib import Path
from typing import Optional

import pytest

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.modules import WeatherEpw
from colibri.modules.air_flows.air_flow_building.air_flow_building import (
    AirFlowBuilding,
)


@pytest.mark.xfail(reason="in progress...")
def test_air_flow_building(case_name: Optional[str] = None) -> None:
    """Test the AirFlowBuilding class."""
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-orchestrator-1",
        iterate_for_convergence=True,
        maximum_number_of_iterations=100,
        time_steps=8_760,
        verbose=False,
    )
    if case_name == "bestest-600":
        pass
    if case_name == "bestest-900":
        pass
    if case_name == "hydraulic-network":
        pass
    if case_name == "pressure-model":
        pass
    project_file_path = ""
    epw_file_path = ""
    project_data: ProjectData = ProjectData(
        name="project-data-1",
        data=project_file_path,
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-1",
        epw_file_path=epw_file_path,
        constant_ground_temperature=10.0,
    )
    project_orchestrator.add_model(model=weather)


@pytest.mark.xfail(reason="in progress...")
def test_air_flow_building_bestest_case() -> None:
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-orchestrator-1",
        iterate_for_convergence=True,
        maximum_number_of_iterations=100,
        time_steps=8_760,
        verbose=False,
    )
    project_file_path: Path = (
        Path(__file__).resolve().parents[3] / "data" / "house_1.json"
    )
    epw_file_path: Path = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "weather"
        / "epw"
        / "Paris.epw"
    )
    project_data: ProjectData = ProjectData(
        name="project-data-1",
        data=project_file_path,
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-1",
        epw_file_path=epw_file_path,
        constant_ground_temperature=10.0,
    )
    project_orchestrator.add_model(model=weather)

    multizone_building = Thermal_Building("thermal model")
    multizone_building.blind_position = 1  # 1 = open
    multizone_building.case = case
    project.add(multizone_building)


if __name__ == "__main__":
    test_air_flow_building_bestest_case()
