"""
Test examples from PPTX of the proof of concept (PoC).
"""

from pathlib import Path

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


def pptx_1_of_poc() -> None:
    """Test example 1 from PPTX of the proof of concept (PoC)."""
    # Create project_orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-orchestrator", verbose=False
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1_poc_pptx_1.json"
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
    weather: WeatherModel = WeatherModel(name="weather")
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
    project_orchestrator.add_plot("Text", weather, "exterior_air_temperature")
    project_orchestrator.add_plot("Tsp", occupants, "setpoint_temperatures")
    project_orchestrator.add_plot("G", occupants, "gains")
    project_orchestrator.add_plot("q_walls", simplified_wall_losses, "q_walls")
    project_orchestrator.add_plot(
        "Tint", thermal_space_simplified, "inside_air_temperatures"
    )
    project_orchestrator.add_plot(
        "q_needs", thermal_space_simplified, "q_needs"
    )
    project_orchestrator.add_plot(
        "q_provided", infinite_power_generator, "q_provided"
    )
    # Run project_orchestrator
    project_orchestrator.run()
    # Plots
    project_orchestrator.plot(show_title=False)


def pptx_2_of_poc() -> None:
    """Test example 1 from PPTX of the proof of concept (PoC)."""
    # Create project_orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-orchestrator", verbose=False
    )
    # Create models
    project_file: Path = (
        Path(__file__).resolve().parents[1] / "data" / "house_1_poc_pptx_2.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    limited_generator: LimitedGenerator = LimitedGenerator(
        name="limited_generator"
    )
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal_space_simplified"
    )
    layer_wall_losses: LayerWallLosses = LayerWallLosses(
        name="layer_wall_losses"
    )
    occupants: OccupantModel = OccupantModel(name="occupants")
    weather: WeatherModel = WeatherModel(name="weather")
    # Add models
    project_orchestrator.add_module(module=project_data)
    project_orchestrator.add_module(module=acv_exploitation_only)
    project_orchestrator.add_module(module=limited_generator)
    project_orchestrator.add_module(module=layer_wall_losses)
    project_orchestrator.add_module(module=thermal_space_simplified)
    project_orchestrator.add_module(module=occupants)
    project_orchestrator.add_module(module=weather)
    # Add links
    project_orchestrator.create_links_automatically()
    # Add plots
    project_orchestrator.add_plot("Text", weather, "exterior_air_temperature")
    project_orchestrator.add_plot("Tsp", occupants, "setpoint_temperatures")
    project_orchestrator.add_plot("G", occupants, "gains")
    project_orchestrator.add_plot("q_walls", layer_wall_losses, "q_walls")
    project_orchestrator.add_plot(
        "Tint", thermal_space_simplified, "inside_air_temperatures"
    )
    project_orchestrator.add_plot(
        "q_needs", thermal_space_simplified, "q_needs"
    )
    project_orchestrator.add_plot("q_provided", limited_generator, "q_provided")
    # Run project_orchestrator
    project_orchestrator.run()
    # Plots
    project_orchestrator.plot(show_title=False)


if __name__ == "__main__":
    pptx_1_of_poc()
    # pptx_2_of_poc()
