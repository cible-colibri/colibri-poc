"""
Tests for the `air_flow_building.py` module.
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from colibri.core import ProjectData, ProjectOrchestrator
from colibri.modules import WeatherEpw
from colibri.modules.air_flows.air_flow_building.air_flow_building import (
    AirFlowBuilding,
)
from colibri.modules.modules_constants import DENSITY_AIR
from colibri.modules.thermal_spaces.detailed_building.thermal_building import (
    ThermalBuilding,
)
from colibri.project_objects import BoundaryCondition


@pytest.mark.xfail(reason="in progress...")
def test_air_flow_building_bestest_case() -> None:
    # Project orchestrator
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-orchestrator-1",
        iterate_for_convergence=True,
        maximum_number_of_iterations=100,
        time_steps=8_760,
        verbose=False,
    )
    # Project data
    # TODO: See later to include flow_paths and boundary conditions
    #       in input file
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
    project_file_path: Path = (
        Path(__file__).resolve().parents[3] / "data" / "house_1.json"
    )
    project_data: ProjectData = ProjectData(
        name="project-data-1",
        data=project_file_path,
    )
    project_data.boundary_conditions = boundary_conditions
    project_orchestrator.add_module(module=project_data)
    # Weather
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
    # Thermal model
    multi_zone_building: ThermalBuilding = ThermalBuilding(name="thermal-model")
    multi_zone_building.blind_position = 1  # 1 = open
    project_orchestrator.add_module(module=multi_zone_building)
    # Air flow model
    air_flow_building: AirFlowBuilding = AirFlowBuilding(
        name="air-flow-model", flow_paths=flow_paths, has_pressure_model=True
    )
    project_orchestrator.add_module(module=air_flow_building)
    # Add links
    project_orchestrator.add_link(
        from_module=weather,
        from_field="sky_temperatures",
        to_module=air_flow_building,
        to_field="sky_temperatures",
    )
    project_orchestrator.add_link(
        from_module=weather,
        from_field="exterior_air_temperatures",
        to_module=air_flow_building,
        to_field="exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        from_module=air_flow_building,
        from_field="flow_rates",
        to_module=multi_zone_building,
        to_field="flow_rates",
    )
    project_orchestrator.add_link(
        from_module=multi_zone_building,
        from_field="space_temperatures",
        to_module=air_flow_building,
        to_field="space_temperatures",
    )
    # Run project orchestrator
    project_orchestrator.run()


if __name__ == "__main__":
    test_air_flow_building_bestest_case()
