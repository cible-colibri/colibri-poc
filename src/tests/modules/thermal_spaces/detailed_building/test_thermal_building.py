"""
Tests for the `thermal_building.py` module.
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.interfaces import Building
from colibri.modules import (
    AirFlowBuilding,
    EmitterProperties,
    ThermalBuilding,
    WeatherEpw,
)
from colibri.modules.modules_constants import DENSITY_AIR
from colibri.project_objects import BoundaryCondition


def test_thermal_building() -> None:
    """Test the thermal_building class."""
    # Create a building (from SimpleBuilding module) and add it to the project orchestrator
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
        time_steps=48,  # 8_760,
        iterate_for_convergence=True,
        maximum_number_of_iterations=100,
    )
    # Create a weather (from Weather module) and add it to the project orchestrator
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
    project_orchestrator.add_module(module=weather)
    # Create project data
    boundary_condition_1: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-1",
        label="living room exterior boundary condition",
        z_relative_position=0,
        pressure=0,
    )
    boundary_condition_2: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-2",
        label="kitchen exterior boundary condition",
        z_relative_position=0,
        pressure=0,
    )
    boundary_conditions: List[BoundaryCondition] = [
        boundary_condition_1,
        boundary_condition_2,
    ]
    project_file: Path = (
        Path(__file__).resolve().parents[3] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project_data", data=project_file
    )
    project_data.boundary_conditions = boundary_conditions
    project_orchestrator.add_module(module=project_data)
    # Create a building (from SimpleBuilding module) and add it to the project orchestrator
    multi_zone_building: ThermalBuilding = ThermalBuilding(
        name="building-1", blind_position=1
    )
    project_orchestrator.add_module(module=multi_zone_building)
    # Add air flow module
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living_room_1"],
            "z": 0,
            "connection": {
                "connection_type": "inlet_grille",
                "dp0": 20,
                "rho0": DENSITY_AIR,
                "flow0": 30,
                "n": 0.5,
            },
        },
        {
            "path": ["living_room_1", "kitchen_1"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen_1", "boundary-condition-2"],
            "z": 0,
            "connection": {
                "connection_type": "outlet_grille",
                "dp0": 80,
                "rho0": DENSITY_AIR,
                "flow0": 45,
                "n": 0.5,
            },
        },
    ]
    air_flow_building: AirFlowBuilding = AirFlowBuilding(
        name="air-flow-1", flow_paths=flow_paths, has_pressure_model=True
    )
    project_orchestrator.add_module(module=air_flow_building)
    # Add emitters' properties module
    emitters_properties: EmitterProperties = EmitterProperties(
        name="emitters-properties-1"
    )
    project_orchestrator.add_module(module=emitters_properties)
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
        weather, "sky_temperatures", multi_zone_building, "sky_temperatures"
    )
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperatures",
        multi_zone_building,
        "exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        weather,
        "rolling_exterior_air_temperatures",
        multi_zone_building,
        "rolling_exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        weather, "direct_radiations", multi_zone_building, "direct_radiations"
    )
    project_orchestrator.add_link(
        weather, "diffuse_radiations", multi_zone_building, "diffuse_radiations"
    )
    project_orchestrator.add_link(
        weather,
        "ground_temperatures",
        multi_zone_building,
        "ground_temperatures",
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
    project_orchestrator.add_link(
        emitters_properties,
        "emitter_properties",
        multi_zone_building,
        "emitter_properties",
    )
    project_orchestrator.add_link(
        multi_zone_building,
        "operating_modes",
        emitters_properties,
        "operating_modes",
    )
    project_orchestrator.add_link(
        multi_zone_building,
        "heat_fluxes",
        emitters_properties,
        "heat_demands",
    )
    # Run project_orchestrator
    project_orchestrator.run()


if __name__ == "__main__":
    test_thermal_building()
    test_thermal_building_case_1()
