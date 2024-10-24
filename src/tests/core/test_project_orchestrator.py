"""
Tests for the `project_orchestrator.py` module.
"""

import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.modules import SimplifiedWallLosses, WeatherModel
from colibri.utils.exceptions_utils import LinkError


@patch("matplotlib.pyplot.show")
def test_project_orchestrator(mock_show: MagicMock) -> None:
    """Test the ProjectOrchestrator class."""
    assert isinstance(mock_show, MagicMock) is True
    project_orchestrator_name_example: str = "project_orchestrator_example"
    project_orchestrator_example: ProjectOrchestrator = ProjectOrchestrator(
        name=project_orchestrator_name_example
    )
    message: dict = project_orchestrator_example.run()
    assert isinstance(message, dict) is True
    project_orchestrator_name_example: str = "project_orchestrator_example"
    project_orchestrator_example: ProjectOrchestrator = ProjectOrchestrator(
        name=project_orchestrator_name_example, verbose=True
    )
    message: dict = project_orchestrator_example.run()
    assert isinstance(message, dict) is True
    # Update project
    project_orchestrator_example.time_steps = 8
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            18.0,
            19.0,
            20.0,
            21.0,
            22.0,
            24.0,
            20.0,
            17.0,
        ],
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    # Add models
    project_orchestrator_example.add_module(module=project_data)
    project_orchestrator_example.add_module(module=simplified_wall_losses)
    project_orchestrator_example.add_module(module=weather)
    # Get models by name
    assert (
        project_orchestrator_example.get_module_by_name(
            name="simplified_wall_losses"
        )
        == simplified_wall_losses
    )
    assert (
        project_orchestrator_example.get_module_by_name(name="wrong_name")
        is None
    )
    # Create link automatically
    project_orchestrator_example.create_links_automatically()
    # Add plots
    project_orchestrator_example.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    # Run project
    project_orchestrator_example.run(show_plots=True)
    assert weather.exterior_air_temperature_series == [
        18.0,
        19.0,
        20.0,
        21.0,
        22.0,
        24.0,
        20.0,
        17.0,
    ]
    assert simplified_wall_losses.q_walls_series[0][
        "Mur salon nord"
    ] == pytest.approx(68.2, abs=1)
    with pytest.raises(LinkError) as exception_information:
        project_orchestrator_example.add_link(
            weather,
            "exterior_air_temperature",
            simplified_wall_losses,
            "exterior_air_temperature",
        )
    assert exception_information.typename == LinkError.__name__
    assert "is already linked to" in str(exception_information.value)


@patch("matplotlib.pyplot.show")
def test_project_orchestrator_with_iterations(mock_show: MagicMock) -> None:
    """Test the ProjectOrchestrator class with iterations."""
    assert isinstance(mock_show, MagicMock) is True
    project_orchestrator_name_example: str = "project_orchestrator_example"
    project_orchestrator_example: ProjectOrchestrator = ProjectOrchestrator(
        name=project_orchestrator_name_example,
        time_steps=8,
        verbose=False,
        iterate_for_convergence=True,
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            18.0,
            19.0,
            20.0,
            21.0,
            22.0,
            24.0,
            20.0,
            17.0,
        ],
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    # Add models
    project_orchestrator_example.add_module(module=project_data)
    project_orchestrator_example.add_module(module=simplified_wall_losses)
    project_orchestrator_example.add_module(module=weather)
    # Create link automatically
    project_orchestrator_example.create_links_automatically()
    # Add plots
    project_orchestrator_example.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    # Run project
    project_orchestrator_example.run(show_plots=True)
    assert weather.exterior_air_temperature_series == [
        18.0,
        19.0,
        20.0,
        21.0,
        22.0,
        24.0,
        20.0,
        17.0,
    ]
    assert simplified_wall_losses.q_walls_series[0][
        "Mur salon nord"
    ] == pytest.approx(68.2, abs=1)
    # Exceed iterations
    project_orchestrator_example_2: ProjectOrchestrator = ProjectOrchestrator(
        name=project_orchestrator_name_example,
        time_steps=8,
        verbose=False,
        iterate_for_convergence=True,
        maximum_number_of_iterations=-1,
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            18.0,
            19.0,
            20.0,
            21.0,
            22.0,
            24.0,
            20.0,
            17.0,
        ],
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    # Add models
    project_orchestrator_example_2.add_module(module=project_data)
    project_orchestrator_example_2.add_module(module=simplified_wall_losses)
    project_orchestrator_example_2.add_module(module=weather)
    # Create link automatically
    project_orchestrator_example_2.create_links_automatically()
    # Add plots
    project_orchestrator_example_2.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    # Run project
    project_orchestrator_example_2.run(show_plots=True)
    assert weather.exterior_air_temperature_series == [
        18.0,
        19.0,
        20.0,
        21.0,
        22.0,
        24.0,
        20.0,
        17.0,
    ]
    assert simplified_wall_losses.q_walls_series[0][
        "Mur salon nord"
    ] == pytest.approx(68.2, abs=1)


def test_project_orchestrator_generate_scheme() -> None:
    """Test the ProjectOrchestrator class' generate_scheme function."""
    module_collection: List[str] = [
        "AcvExploitationOnly",
        "LimitedGenerator",
        "OccupantModel",
        "LayerWallLosses",
        "ThermalSpaceSimplified",
        "WeatherModel",
    ]
    scheme = ProjectOrchestrator.generate_scheme(modules=module_collection)
    assert set(scheme.keys()) == set(
        [
            "BoundaryObject",
            "ElementObject",
            "Modules",
            "StructureObject",
            "Archetype",
        ]
    )
    assert set(scheme["StructureObject"].keys()) == set(
        [
            "Boundary",
            "BoundaryCondition",
            "Building",
            "LinearJunction",
            "PunctualJunction",
            "Project",
            "Segment",
            "Space",
        ]
    )
    assert set(scheme["BoundaryObject"].keys()) == set(
        [
            "Emitter",
        ]
    )
    assert set(scheme["Modules"].keys()) == set(
        [
            "AcvExploitationOnly",
            "OccupantModel",
            "WeatherModel",
        ]
    )
    assert set(scheme["Archetype"].keys()) == set(
        [
            "Emitter",
            "Boundary",
            "Layer",
        ]
    )
    assert set(scheme["ElementObject"].keys()) == set(
        [
            "layers",
        ]
    )