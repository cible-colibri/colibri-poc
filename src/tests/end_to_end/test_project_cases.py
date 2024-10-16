"""
Test cases for the `project_orchestrator.py` module.
"""

from pathlib import Path
from random import randint
from unittest.mock import MagicMock, patch

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.modules import (
    AcvExploitationOnly,
    InfinitePowerGenerator,
    LayerWallLosses,
    LimitedGenerator,
    OccupantModel,
    SimplifiedWallLosses,
    ThermalSpaceSimplified,
    WeatherModel,
)


@patch("matplotlib.pyplot.show")
def test_prototype_with_links(mock_show: MagicMock) -> None:
    """Test a prototype with links."""
    assert isinstance(mock_show, MagicMock) is True
    # Create project_orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="my-project-orchestrator", verbose=False
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    infinite_power_generator: InfinitePowerGenerator = InfinitePowerGenerator(
        name="infinite_power_generator"
    )
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal_space_simplified"
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    occupants: OccupantModel = OccupantModel(name="occupants")
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            randint(5, 20) for _ in range(0, project_orchestrator.time_steps)
        ],
    )
    # Add models
    project_orchestrator.add_module(module=project_data)
    project_orchestrator.add_module(module=acv_exploitation_only)
    project_orchestrator.add_module(module=infinite_power_generator)
    project_orchestrator.add_module(module=simplified_wall_losses)
    project_orchestrator.add_module(module=thermal_space_simplified)
    project_orchestrator.add_module(module=occupants)
    project_orchestrator.add_module(module=weather)
    # Add links
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperature",
        simplified_wall_losses,
        "exterior_air_temperature",
    )
    project_orchestrator.add_link(
        thermal_space_simplified,
        "inside_air_temperatures",
        simplified_wall_losses,
        "inside_air_temperatures",
    )
    project_orchestrator.add_link(
        simplified_wall_losses, "q_walls", thermal_space_simplified, "q_walls"
    )
    project_orchestrator.add_link(
        thermal_space_simplified,
        "q_needs",
        infinite_power_generator,
        "q_needs",
    )
    project_orchestrator.add_link(
        infinite_power_generator,
        "q_provided",
        thermal_space_simplified,
        "q_provided",
    )
    project_orchestrator.add_link(
        infinite_power_generator,
        "q_consumed",
        acv_exploitation_only,
        "q_consumed",
    )
    project_orchestrator.add_link(
        occupants,
        "setpoint_temperatures",
        thermal_space_simplified,
        "setpoint_temperatures",
    )
    project_orchestrator.add_link(
        occupants, "gains", thermal_space_simplified, "gains"
    )
    # Add plots
    project_orchestrator.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    project_orchestrator.add_plot(
        "Tint", thermal_space_simplified, "inside_air_temperatures"
    )
    project_orchestrator.add_plot("Qwall", simplified_wall_losses, "q_walls")
    project_orchestrator.add_plot(
        "Qprovided", infinite_power_generator, "q_provided"
    )
    # Run project_orchestrator
    project_orchestrator.run()
    # Plots
    project_orchestrator.plot()


@patch("matplotlib.pyplot.show")
def test_prototype_with_links_created_automatically(
    mock_show: MagicMock,
) -> None:
    """Test a prototype with links created automatically."""
    assert isinstance(mock_show, MagicMock) is True
    # Create project_orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="my-project-orchestrator", verbose=False
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    infinite_power_generator: InfinitePowerGenerator = InfinitePowerGenerator(
        name="infinite_power_generator"
    )
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal_space_simplified"
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    occupants: OccupantModel = OccupantModel(name="occupants")
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            randint(5, 20) for _ in range(0, project_orchestrator.time_steps)
        ],
    )
    # Add models
    project_orchestrator.add_module(module=project_data)
    project_orchestrator.add_module(module=acv_exploitation_only)
    project_orchestrator.add_module(module=infinite_power_generator)
    project_orchestrator.add_module(module=simplified_wall_losses)
    project_orchestrator.add_module(module=thermal_space_simplified)
    project_orchestrator.add_module(module=occupants)
    project_orchestrator.add_module(module=weather)
    # Add links
    project_orchestrator.create_links_automatically()
    # Add plots
    project_orchestrator.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    project_orchestrator.add_plot(
        "Tint", thermal_space_simplified, "inside_air_temperatures"
    )
    project_orchestrator.add_plot("Qwall", simplified_wall_losses, "q_walls")
    project_orchestrator.add_plot(
        "Qprovided", infinite_power_generator, "q_provided"
    )
    # Run project_orchestrator
    project_orchestrator.run()
    # Plots
    project_orchestrator.plot()


@patch("matplotlib.pyplot.show")
def test_prototype_variant_with_links_automatically(
    mock_show: MagicMock,
) -> None:
    """Test a prototype's variant with links created automatically."""
    assert isinstance(mock_show, MagicMock) is True
    # Create project_orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="my-project-orchestrator", verbose=False
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    limited_power_generator: LimitedGenerator = LimitedGenerator(
        name="limited_power_generator"
    )
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal_space_simplified"
    )
    layer_wall_losses: LayerWallLosses = LayerWallLosses(
        name="layer_wall_losses"
    )
    occupants: OccupantModel = OccupantModel(name="occupants")
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            randint(5, 20) for _ in range(0, project_orchestrator.time_steps)
        ],
    )
    # Add models
    project_orchestrator.add_module(module=project_data)
    project_orchestrator.add_module(module=acv_exploitation_only)
    project_orchestrator.add_module(module=limited_power_generator)
    project_orchestrator.add_module(module=layer_wall_losses)
    project_orchestrator.add_module(module=thermal_space_simplified)
    project_orchestrator.add_module(module=occupants)
    project_orchestrator.add_module(module=weather)
    # Add links
    project_orchestrator.create_links_automatically()
    # Add plots
    project_orchestrator.add_plot(
        "Weather", weather, "exterior_air_temperature"
    )
    project_orchestrator.add_plot(
        "Tint", thermal_space_simplified, "inside_air_temperatures"
    )
    project_orchestrator.add_plot("Qwall", layer_wall_losses, "q_walls")
    project_orchestrator.add_plot(
        "Qprovided", limited_power_generator, "q_provided"
    )
    # Run project_orchestrator
    project_orchestrator.run()
    # Plots
    project_orchestrator.plot()


if __name__ == "__main__":
    test_prototype_with_links()
    test_prototype_with_links_created_automatically()
    test_prototype_variant_with_links_automatically()
