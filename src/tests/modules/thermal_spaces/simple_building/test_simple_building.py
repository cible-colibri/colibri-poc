"""
Tests for the `simple_building.py` module.
"""

from pathlib import Path
from typing import List

import numpy as np
import pytest

from colibri.core import ProjectOrchestrator
from colibri.interfaces import ThermalSpace
from colibri.modules import (
    SimpleBuilding,
    WeatherEpw,
)


def test_simple_building_heating_only() -> None:
    """Test the SimpleBuilding class."""
    # Create a project orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-1",
        time_steps=20,  # Set time steps
        iterate_for_convergence=False,  # Set no loops (runs twice as fast)
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
        name="weather-1", epw_file_path=epw_file_path
    )
    project_orchestrator.add_module(module=weather)
    # Create a building (from SimpleBuilding model) and add it to the project orchestrator
    building: SimpleBuilding = SimpleBuilding("building-1")
    project_orchestrator.add_module(module=building)
    # Link temperature and radiation from weather to building (for post-initialization)
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperatures",
        building,
        "exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiations",
        building,
        "global_horizontal_radiations",
    )
    # Link temperature and radiation from weather to building
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperature",
        building,
        "exterior_air_temperature",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiation",
        building,
        "global_horizontal_radiation",
    )
    # Run project
    project_orchestrator.run()
    assert isinstance(building, ThermalSpace) is True
    assert isinstance(building, SimpleBuilding) is True
    expected_temperature_series: List[float] = [
        4.0,
        6.9,
        8.3,
        9.3,
        9.9,
        10.1,
        10.3,
        10.2,
        10.2,
        10.1,
        10.4,
        11.3,
        12.0,
        12.5,
        12.6,
        12.3,
        11.8,
        11.2,
        10.9,
        10.9,
    ]
    for index, zone_temperature in enumerate(building.zone_temperature_series):
        assert zone_temperature == pytest.approx(
            expected_temperature_series[index], abs=0.2
        )


def test_simple_building_cooling_only() -> None:
    """Test the SimpleBuilding class."""
    # Create a project orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-1",
        time_steps=20,  # Set time steps
        iterate_for_convergence=False,  # Set no loops (runs twice as fast)
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
        name="weather-1", epw_file_path=epw_file_path
    )
    project_orchestrator.add_module(module=weather)
    # Create a building (from SimpleBuilding model) and add it to the project orchestrator
    building: SimpleBuilding = SimpleBuilding(
        "building-1",
        is_cooling_on=True,
        is_heating_on=False,
    )
    project_orchestrator.add_module(module=building)
    # Link temperature and radiation from weather to building (for post-initialization)
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperatures",
        building,
        "exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiations",
        building,
        "global_horizontal_radiations",
    )
    # Link temperature and radiation from weather to building
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperature",
        building,
        "exterior_air_temperature",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiation",
        building,
        "global_horizontal_radiation",
    )
    # Run project
    project_orchestrator.run()
    assert isinstance(building, ThermalSpace) is True
    assert isinstance(building, SimpleBuilding) is True
    assert max(building.zone_temperature_series) == pytest.approx(27, abs=0.2)
    assert min(building.zone_temperature_series) == pytest.approx(20, abs=0.2)
    assert np.median(building.zone_temperature_series) == pytest.approx(
        27, abs=0.2
    )
    assert building.has_converged(time_step=1, number_of_iterations=1) is True


if __name__ == "__main__":
    test_simple_building_heating_only()
    test_simple_building_cooling_only()
