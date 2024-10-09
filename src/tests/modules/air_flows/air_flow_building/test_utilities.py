"""
Tests for the `utilities.py` module.
"""

from typing import Any, Dict, List

import pytest

from colibri.modules.air_flows.air_flow_building.utilities import (
    construct_boundary_and_space_nodes,
    construct_flow_resistance_coefficient_matrices,
    get_fan_suction_nodes,
)
from colibri.modules.modules_constants import DENSITY_AIR
from colibri.project_objects import BoundaryCondition, Space


def test_construct_boundary_and_space_nodes() -> None:
    """Test the compute_door_back_pressure_coefficient function."""
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=23.8,
        reference_area=9.52,
    )
    space_2: Space = Space(
        id="living-room",
        label="living-room",
        volume=52.25,
        reference_area=20.9,
    )
    spaces: List[Space] = [space_1, space_2]
    boundary_condition_1: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-1",
        label="kitchen exterior boundary condition",
        pressure=0,
    )
    boundary_condition_2: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-2",
        label="living room exterior boundary condition",
        pressure=0,
    )
    boundary_conditions: List[BoundaryCondition] = [
        boundary_condition_1,
        boundary_condition_2,
    ]
    (
        boundary_condition_indices,
        boundary_condition_names,
        boundary_condition_pressures,
        space_indices,
        space_names,
    ) = construct_boundary_and_space_nodes(
        spaces=spaces, boundary_conditions=boundary_conditions
    )
    assert boundary_condition_indices == [0, 1]
    assert boundary_condition_names == [
        "boundary-condition-1",
        "boundary-condition-2",
    ]
    assert boundary_condition_pressures == [0, 0]
    assert space_indices == [0, 1]
    assert space_names == ["kitchen", "living-room"]


def test_construct_flow_resistance_coefficient_matrices() -> None:
    """Test the compute_dtu_duct_pressure_loss function."""
    # Test no. 1
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
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
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen", "boundary-condition-2"],
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
    (
        space_flow_resistance_nodes,
        boundary_and_space_flow_resistance_nodes,
        exponent_space_flow_resistance_nodes,
        exponent_boundary_and_space_flow_resistance_nodes,
        imposed_flow_rates,
        flows,
        fans,
    ) = construct_flow_resistance_coefficient_matrices(
        flow_paths=flow_paths,
        boundary_condition_names=[
            "boundary-condition-1",
            "boundary-condition-2",
        ],
        space_names=["kitchen", "living-room"],
    )
    assert space_flow_resistance_nodes[0][0] == pytest.approx(0.0, abs=0.01)
    assert boundary_and_space_flow_resistance_nodes[0][0] == pytest.approx(
        0.0, abs=0.01
    )
    assert exponent_space_flow_resistance_nodes[0][1] == pytest.approx(
        0.5, abs=0.01
    )
    assert exponent_boundary_and_space_flow_resistance_nodes[0][
        1
    ] == pytest.approx(0.5, abs=0.01)
    assert imposed_flow_rates[0][0] == pytest.approx(0.0, abs=0.01)
    assert flows == []
    assert fans == []
    # Test no. 2
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
            "z": 0,
            "connection": {
                "connection_type": "fan",
                "dp0": 20,
                "rho0": DENSITY_AIR,
                "flow0": 30,
                "n": 0.5,
            },
        },
        {
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen", "boundary-condition-2"],
            "z": 0,
            "connection": {
                "connection_type": "flow",
                "dp0": 80,
                "rho0": DENSITY_AIR,
                "flow0": 45,
                "n": 0.5,
            },
        },
    ]
    (
        space_flow_resistance_nodes,
        boundary_and_space_flow_resistance_nodes,
        exponent_space_flow_resistance_nodes,
        exponent_boundary_and_space_flow_resistance_nodes,
        imposed_flow_rates,
        flows,
        fans,
    ) = construct_flow_resistance_coefficient_matrices(
        flow_paths=flow_paths,
        boundary_condition_names=[
            "boundary-condition-1",
            "boundary-condition-2",
        ],
        space_names=["kitchen", "living-room"],
    )
    assert space_flow_resistance_nodes[0][0] == pytest.approx(0.0, abs=0.01)
    assert boundary_and_space_flow_resistance_nodes[0][0] == pytest.approx(
        0.0, abs=0.01
    )
    assert exponent_space_flow_resistance_nodes[0][1] == pytest.approx(
        0.5, abs=0.01
    )
    assert exponent_boundary_and_space_flow_resistance_nodes[0][
        1
    ] == pytest.approx(0.0, abs=0.01)
    assert exponent_boundary_and_space_flow_resistance_nodes[1][
        0
    ] == pytest.approx(0.5, abs=0.01)
    assert imposed_flow_rates[0][0] == pytest.approx(0.0, abs=0.01)
    assert flows[0][0]["path"] == ["kitchen", "boundary-condition-2"]
    assert flows[0][1] == 1
    assert flows[0][2] == "boundary-condition-2"
    assert flows[0][3] == 0
    assert fans[0][0]["path"] == ["boundary-condition-1", "living-room"]
    assert fans[0][1] == 0
    assert fans[0][2] == "boundary-condition-1"
    assert fans[0][3] == 1
    # Test no. 3
    wrong_flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "boundary-condition-2"],
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
    with pytest.raises(ValueError) as exception_information:
        _ = construct_flow_resistance_coefficient_matrices(
            flow_paths=wrong_flow_paths,
            boundary_condition_names=[
                "boundary-condition-1",
                "boundary-condition-2",
            ],
            space_names=["kitchen", "living-room"],
        )
    assert exception_information.typename == ValueError.__name__
    assert "Two external pressure nodes cannot be connected together" in str(
        exception_information.value
    )


def test_get_fan_suction_nodes() -> None:
    """Test the get_fan_suction_nodes function."""
    # Test no. 1
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
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
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen", "boundary-condition-2"],
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
    fan_suction_nodes: List[str] = get_fan_suction_nodes(
        flow_paths=flow_paths,
        boundary_condition_names=[
            "boundary-condition-1",
            "boundary-condition-2",
        ],
    )
    assert fan_suction_nodes == []
    # Test no. 2
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
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
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["boundary-condition-2", "kitchen"],
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
    fan_suction_nodes: List[str] = get_fan_suction_nodes(
        flow_paths=flow_paths,
        boundary_condition_names=[
            "boundary-condition-1",
            "boundary-condition-2",
        ],
    )
    assert fan_suction_nodes == []
    # Test no. 3
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
            "z": 0,
            "connection": {
                "connection_type": "fan",
                "dp0": 20,
                "rho0": DENSITY_AIR,
                "flow0": 30,
                "n": 0.5,
            },
        },
        {
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen", "boundary-condition-2"],
            "z": 0,
            "connection": {
                "connection_type": "flow",
                "dp0": 80,
                "rho0": DENSITY_AIR,
                "flow0": 45,
                "n": 0.5,
            },
        },
    ]
    fan_suction_nodes: List[str] = get_fan_suction_nodes(
        flow_paths=flow_paths,
        boundary_condition_names=[
            "boundary-condition-1",
            "boundary-condition-2",
        ],
    )
    assert fan_suction_nodes == ["boundary-condition-1"]
    # Test no. 4
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "fan",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
    ]
    with pytest.raises(ValueError) as exception_information:
        _ = get_fan_suction_nodes(
            flow_paths=flow_paths,
            boundary_condition_names=[
                "boundary-condition-1",
                "boundary-condition-2",
            ],
        )
    assert exception_information.typename == ValueError.__name__
    assert "is not connected to an external boundary pressure" in str(
        exception_information.value
    )


if __name__ == "__main__":
    test_construct_boundary_and_space_nodes()
    test_construct_flow_resistance_coefficient_matrices()
    test_get_fan_suction_nodes()
