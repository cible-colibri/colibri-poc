"""
Utility functions for the air flow building.
"""

import copy
from enum import Enum, unique
from typing import Any, Dict, List, Set, Tuple

import numpy as np
from numpy import ndarray
from scipy.linalg import inv

from colibri.config.constants import UNIT_CONVERTER
from colibri.modules.air_flows.air_flow_building.connection_functions import (
    compute_door_back_pressure_coefficient,
    compute_dtu_duct_pressure_loss,
    compute_grille_back_pressure_coefficient,
)
from colibri.modules.modules_constants import (
    ATMOSPHERIC_AIR_PRESSURE,
    DENSITY_AIR,
    GRAVITATIONAL_ACCELERATION,
    RS_AIR,
)
from colibri.project_objects import BoundaryCondition, Space
from colibri.utils.enums_utils import Units


@unique
class FlowConnectionTypes(Enum):
    DOOR = "door"
    DUCT = "duct"
    FAN = "fan"
    FLOW = "flow"
    GRILLE = "grille"


def construct_boundary_and_space_nodes(
    spaces: List[Space], boundary_conditions: List[BoundaryCondition]
) -> Tuple[List[int], List[str], List[float], List[int], List[str]]:
    """Compute boundary and space nodes' information

    Parameters
    ----------
    spaces : List[Space]
        List of spaces
    boundary_conditions : List[BoundaryCondition]
        List of boundary conditions

    Returns
    -------
    Tuple[List[int], List[str], List[float], List[int], List[str]]:
        boundary_condition_indices : List[int]
            Boundary condition indices
        boundary_condition_names : List[str]
            Boundary condition names/ids
        boundary_condition_pressures : List[float]
            Pressure associated with each boundary condition
        space_indices : List[int]
            Space indices
        space_names :  List[str]
            Space names/ids

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    boundary_condition_indices: List[str] = []
    boundary_condition_names: List[str] = []
    boundary_condition_pressures: List[float] = []
    space_indices: List[str] = []
    space_names: List[str] = []
    for space_index, space in enumerate(spaces):
        space_indices.append(space_index)
        space_names.append(space.id)
    for boundary_condition_index, boundary_condition in enumerate(
        boundary_conditions
    ):
        boundary_condition_indices.append(boundary_condition_index)
        boundary_condition_names.append(boundary_condition.id)
        boundary_condition_pressures.append(boundary_condition.pressure)
    return (
        boundary_condition_indices,
        boundary_condition_names,
        boundary_condition_pressures,
        space_indices,
        space_names,
    )


def construct_flow_resistance_coefficient_matrices(
    flow_paths: Dict[str, Dict[str, Any]],
    boundary_condition_names: List[str],
    space_names: List[str],
) -> ndarray:
    """Construct flow resistance coefficient matrices

    Parameters
    ----------
    flow_paths : Dict[str, Dict[str, Any]]
        Information about the flow paths
    boundary_condition_names : List[str]
        Boundary condition names/ids
    space_names :  List[str]
        Space names/ids

    Returns
    -------
    Tuple[List[int], List[str], List[float], List[int], List[str]]:
        boundary_condition_indices : List[int]
            Boundary condition indices
        boundary_condition_names : List[str]
            Boundary condition names/ids
        boundary_condition_pressures : List[float]
            Pressure associated with each boundary condition
        space_indices : List[int]
            Space indices
        space_names :  List[str]
            Space names/ids

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Retrieve information from spaces and boundary conditions
    number_of_spaces: int = len(space_names)
    number_of_boundary_conditions: int = len(boundary_condition_names)
    # Matrices for air exchange due to pressure differences
    space_flow_resistance_nodes: ndarray = np.zeros(
        (number_of_spaces, number_of_spaces)
    )
    # Number of columns corresponding to external pressure nodes
    boundary_and_space_flow_resistance_nodes: ndarray = np.zeros(
        (number_of_spaces, number_of_boundary_conditions)
    )
    # Exponent matrices for air exchange calculations (with n for dp=C*flow**n)
    exponent_space_flow_resistance_nodes: ndarray = np.zeros(
        (number_of_spaces, number_of_spaces)
    )
    exponent_boundary_and_space_flow_resistance_nodes: ndarray = np.zeros(
        (number_of_spaces, number_of_boundary_conditions)
    )
    # Flow rate matrix for imposed flow rates
    # Number of columns corresponding to external pressure nodes to which the fans can be connected
    imposed_flow_rates: ndarray = np.zeros(
        (number_of_spaces, number_of_boundary_conditions)
    )
    # Array with necessary data for imposed flow rates
    flows: List[int] = []
    # Fan matrix for calculation pressure gains
    # (array with necessary data for imposed flow rates)
    fans: List[int] = []
    for flow_path in flow_paths:
        id_0_name: str = flow_path["path"][0]
        id_1_name: str = flow_path["path"][1]
        # Check that at least one node is inside the system
        id_0_inside: bool = id_0_name in space_names
        id_1_inside: bool = id_1_name in space_names
        if not id_0_inside and not id_1_inside:
            raise ValueError(
                "Two external pressure nodes cannot be connected together. "
                "Please, check you project input file."
            )
        # Compute of back pressure coefficient (kb) value
        connection: Dict[str, Any] = flow_path["connection"]
        connection_type: str = connection["connection_type"]
        if connection_type == "door":
            back_pressure_coefficient: float = (
                compute_door_back_pressure_coefficient(
                    section=connection["section"],
                    discharge_coefficient=connection["discharge_coefficient"],
                    opening=1.0,
                )
            )
            # Exchange coefficient before multiplying with flow rate
            value: float = np.abs(
                back_pressure_coefficient ** (1 / connection["n"]) / DENSITY_AIR
            )
            n_flow: float = connection["n"]
        # Outlet or inlet_grille, same equations
        if "grille" in connection_type:
            back_pressure_coefficient: float = (
                compute_grille_back_pressure_coefficient(
                    dp_0=connection["dp0"],
                    rho_0=connection["rho0"],
                    flow_0=connection["flow0"],
                    n=connection["n"],
                    opening=1.0,
                )
            )
            # Exchange coefficient before multiplying with flow rate
            value: float = np.abs(
                back_pressure_coefficient ** (1 / connection["n"]) / DENSITY_AIR
            )
            n_flow: float = connection["n"]
        if "duct_dtu" in connection_type:
            # Exchange coefficient before multiplying with flow rate
            # No impact if the function is used with type="c_lin"
            nominal_flow_rate: float = 50.0
            value: float = np.abs(
                compute_dtu_duct_pressure_loss(
                    flow_rate=nominal_flow_rate,
                    density=DENSITY_AIR,
                    section=connection["section"],
                    hydraulic_diameter=connection["h_diam"],
                    length=connection["length"],
                    friction_factor=connection["coefK"],
                    pressure_drop_coefficients=connection["dzeta"],
                    computation_mode="c_lin",
                )
            )
            n_flow: float = 0.5
        # Keep 0 values in space_flow_resistance_nodes (CCa)
        # and boundary_and_space_flow_resistance_nodes (CCb)
        # since flow rate is calculated in the fan models and
        # imposed directly as FAN flow rates.
        if "flow" in connection_type:
            value = 1
        if "fan" in connection_type:
            value: float = 1
            n_flow: float = 0.5

        # Check if both nodes are in the space or one boundary condition,
        # either put it in space_flow_resistance_nodes (CCa) or
        # boundary_and_space_flow_resistance_nodes (CCb) + diagonal
        # in space_flow_resistance_nodes
        # Connect to external node via
        # boundary_and_space_flow_resistance_nodes (CCb)
        if id_0_inside and id_1_inside:
            id_0: int = space_names.index(id_0_name)
            id_1: int = space_names.index(id_1_name)
            if ("flow" not in connection_type) and (
                "fan" not in connection_type
            ):
                space_flow_resistance_nodes[id_0, id_1] = value
                space_flow_resistance_nodes[id_1, id_0] = value
                exponent_space_flow_resistance_nodes[id_0, id_1] = n_flow
                exponent_space_flow_resistance_nodes[id_1, id_0] = n_flow
            else:
                assert ValueError(
                    "Fans are not supposed to blow between zones inside the buildings, "
                    "but only between boundary conditions and zones."
                )
            flow_path["flow_matrix"] = "FFa"
            flow_path["flow_sign"] = -1
            flow_path["path_ids"] = [id_1, id_0]
        # Both nodes are in the system, thus only fill in space_flow_resistance_nodes
        if id_0_inside and not id_1_inside:
            flow_sign: int = 1
            id_0: int = space_names.index(id_0_name)
            id_1: int = boundary_condition_names.index(id_1_name)
            if "flow" not in connection_type:
                boundary_and_space_flow_resistance_nodes[id_0, id_1] = value
                exponent_boundary_and_space_flow_resistance_nodes[
                    id_0, id_1
                ] = n_flow
            else:
                # 1 in case of imposed_flow_rates,
                # flow rate of this fan is in the U_flow array
                imposed_flow_rates[id_0, id_1] = -value
                # Save name of flow path to get directly to the fan model saved in the flow path
                flows.append([flow_path, id_1, id_1_name, id_0])
            if "fan" in connection_type:
                # Save name of flow path to get directly to the fan model saved in the flow path
                fans.append([flow_path, id_1, id_1_name, id_0, flow_sign])
            flow_path["flow_matrix"] = "FFb"
            flow_path["flow_sign"] = flow_sign
            flow_path["path_ids"] = [id_0, id_1]
        if id_1_inside and not id_0_inside:
            flow_sign: int = -1
            id_0: int = boundary_condition_names.index(id_0_name)
            id_1: int = space_names.index(id_1_name)
            if "flow" not in connection_type:
                boundary_and_space_flow_resistance_nodes[id_1, id_0] = value
                exponent_boundary_and_space_flow_resistance_nodes[
                    id_1, id_0
                ] = n_flow
            else:
                # 1 in case of imposed_flow_rates,
                # flow rate of this fan is in the U_flow array
                imposed_flow_rates[id_1, id_0] = value
                # Save name of flow path to get directly to the fan model saved in the flow path
                flows.append([flow_path, id_0, id_0_name, id_1])
            if "fan" in connection_type:
                # Save name of flow path to get directly to the fan model saved in the flow path
                fans.append([flow_path, id_0, id_0_name, id_1, flow_sign])
            flow_path["flow_matrix"] = "FFb"
            flow_path["flow_sign"] = flow_sign
            flow_path["path_ids"] = [id_1, id_0]
    return (
        space_flow_resistance_nodes,
        boundary_and_space_flow_resistance_nodes,
        exponent_space_flow_resistance_nodes,
        exponent_boundary_and_space_flow_resistance_nodes,
        imposed_flow_rates,
        flows,
        fans,
    )


def get_fan_suction_nodes(
    flow_paths: Dict[str, Dict[str, Any]], boundary_condition_names: List[str]
) -> List[str]:
    """Construct flow resistance coefficient matrices

    Parameters
    ----------
    flow_paths : Dict[str, Dict[str, Any]]
        Information about the flow paths
    boundary_condition_names : List[str]
        Boundary condition names/ids

    Returns
    -------
    List[str]
        Fan suction nodes

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    fan_suction_nodes: Set[str] = set()
    other_inlet_nodes: Set[str] = set()
    for flow_path in flow_paths:
        id_0_name: str = flow_path["path"][0]
        id_1_name: str = flow_path["path"][1]
        if "fan" in flow_path["connection"]["connection_type"]:
            if id_0_name in boundary_condition_names:
                fan_suction_nodes.add(id_0_name)
            elif id_1_name in boundary_condition_names:
                fan_suction_nodes.add(id_1_name)
            else:
                raise ValueError(
                    f"The fan in flow path '{flow_path['path']}' is not connected to "
                    f"an external boundary pressure. "
                    f"Please, verify your configuration."
                )
        # Other flow path than fan
        else:
            if id_0_name in boundary_condition_names:
                other_inlet_nodes.add(id_0_name)
            elif id_1_name in boundary_condition_names:
                other_inlet_nodes.add(id_1_name)
    # Check that the boundary pressure for each fan suction is unique
    common_elements: Set[str] = fan_suction_nodes.intersection(
        other_inlet_nodes
    )
    if len(common_elements) >= 1:
        raise ValueError(
            "Fan boundary node is also a boundary node for another inlet, "
            "which is not allowed. Please, specify another boundary node."
        )
    return list(fan_suction_nodes)


def generate_relaxation_space_flow_resistance_nodes(
    space_flow_resistance_nodes: ndarray,
    boundary_and_space_flow_resistance_nodes: ndarray,
    connectivity_space_flow_resistance_nodes: ndarray,
    connectivity_boundary_and_space_flow_resistance_nodes: ndarray,
    exponent_space_flow_resistance_nodes: ndarray,
    exponent_boundary_and_space_flow_resistance_nodes: ndarray,
    relaxation_space_flow_matrices: ndarray,
    relaxation_boundary_condition_flow_matrices: ndarray,
) -> Tuple[ndarray, ndarray]:
    """Generate relaxation boundary and space flow resistance (CC) matrices
     with pressure drop coefficients, which are used later to construct A
     matrix of pressure system

    Parameters
    ----------
    space_flow_resistance_nodes : ndarray
    boundary_and_space_flow_resistance_nodes : ndarray
    connectivity_space_flow_resistance_nodes : ndarray
    exponent_space_flow_resistance_nodes : ndarray
    exponent_boundary_and_space_flow_resistance_nodes : ndarray
    connectivity_boundary_and_space_flow_resistance_nodes : ndarray
    relaxation_space_flow_matrices : ndarray
    relaxation_boundary_condition_flow_matrices : ndarray

    Returns
    -------
    List[str]
        Fan suction nodes

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # CCa_act
    relaxation_space_flow_resistance_nodes: ndarray = copy.deepcopy(
        space_flow_resistance_nodes
    )
    # CCb_act
    relaxation_boundary_and_space_flow_resistance_nodes: ndarray = (
        copy.deepcopy(boundary_and_space_flow_resistance_nodes)
    )
    # Go through connectivity table (avoid check for zeros at each time)
    for connection in connectivity_space_flow_resistance_nodes:
        flow_rate: float = np.abs(
            relaxation_space_flow_matrices[connection[0], connection[1]]
        )
        flow_rate = max(abs(flow_rate), 1e-3)
        # dp = C * flow ^ (1/n)
        # changed to: dp = C_act * flow
        # with C_act = C*flow ** (1/n-1)
        n = exponent_space_flow_resistance_nodes[connection[0], connection[1]]
        # Compute the pressure drop coefficients.
        # For a segment, dp = C * flow ^ (1/n)
        relaxation_space_flow_resistance_nodes[
            connection[0], connection[1]
        ] /= flow_rate ** (1 / n - 1)
    # Go through connectivity table (avoid check for zeros at each time)
    for connection in connectivity_boundary_and_space_flow_resistance_nodes:
        flow_rate: float = np.abs(
            relaxation_boundary_condition_flow_matrices[
                connection[0], connection[1]
            ]
        )
        flow_rate = max(abs(flow_rate), 1e-3)
        n = exponent_boundary_and_space_flow_resistance_nodes[
            connection[0], connection[1]
        ]
        # Compute the pressure drop coefficients.
        # For a segment, dp = C * flow ^ (1/n)
        relaxation_boundary_and_space_flow_resistance_nodes[
            connection[0], connection[1]
        ] /= flow_rate ** (1 / n - 1)
    return (
        relaxation_space_flow_resistance_nodes,
        relaxation_boundary_and_space_flow_resistance_nodes,
    )


def generate_system_and_control_pressure_matrices(
    boundary_pressures,
    boundary_flows,
    relaxation_space_flow_resistance_nodes,
    relaxation_boundary_and_space_flow_resistance_nodes,
    imposed_flow_rates,
    flow_paths,
    spaces,
    boundary_conditions,
    space_temperatures,
) -> Tuple[ndarray, ndarray, ndarray]:
    """
    Generate A and B matrices to solve the pressure system : AP + BU = 0

    :param U: fan flowrates and boundary pressures
    :param relaxation_space_flow_resistance_nodes: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment resistance flow coefficients
    :param nnodes: number of nodes in the network
    :param fan_list: list of [j, i] nodes for fan location
    :param inlet_pressure_ids: list of external pressure nodes

    :return: pressures: pressure array of all system nodes
    :return: flowrates: matrix with flow rates between all system nodes
    :return: flowrates_boundary: matrix with flow rates between all boundary and system nodes

    """
    # Generate system pressure (A) matrix and control pressure (B) matrix
    system_pressure_matrix: ndarray = copy.deepcopy(
        relaxation_space_flow_resistance_nodes
    )
    control_pressure_matrix: ndarray = copy.deepcopy(
        relaxation_boundary_and_space_flow_resistance_nodes
    )
    # Set diagonal of system pressure (A) matrix
    # Leaving pressure potential go through columns
    for index, column in enumerate(relaxation_space_flow_resistance_nodes):
        system_pressure_matrix[index, index] = -np.sum(column) - np.sum(
            control_pressure_matrix[index, :]
        )
    pressures, flow_rates, boundary_condition_flow_rates = (
        solve_pressure_system(
            system_pressure_matrix=system_pressure_matrix,
            control_pressure_matrix=control_pressure_matrix,
            relaxation_space_flow_resistance_nodes=relaxation_space_flow_resistance_nodes,
            relaxation_boundary_and_space_flow_resistance_nodes=relaxation_boundary_and_space_flow_resistance_nodes,
            imposed_flow_rates=imposed_flow_rates,
            boundary_pressures=boundary_pressures,
            boundary_flows=boundary_flows,
            flow_paths=flow_paths,
            spaces=spaces,
            boundary_conditions=boundary_conditions,
            space_temperatures=space_temperatures,
        )
    )
    return pressures, flow_rates, boundary_condition_flow_rates


def solve_pressure_system(
    system_pressure_matrix,
    control_pressure_matrix,
    relaxation_space_flow_resistance_nodes,
    relaxation_boundary_and_space_flow_resistance_nodes,
    imposed_flow_rates,
    boundary_pressures,
    boundary_flows,
    flow_paths,
    spaces,
    boundary_conditions,
    space_temperatures,
    buoyancy: bool = True,
) -> Tuple[ndarray, ndarray, ndarray]:
    nodes_size: int = np.shape(control_pressure_matrix)[0]
    boundary_conditions_size: int = len(boundary_pressures)
    nodes: List[Any] = boundary_conditions + spaces
    if buoyancy:
        # Initialize matrices for corrective pressure difference due to
        # buoyancy of connection height
        # Corrections for flow paths inside system nodes
        system_buoyancy_pressure_differences: ndarray = np.zeros(
            (nodes_size, nodes_size)
        )
        # Corrections for flow paths between system nodes and boundary nodes
        system_and_boundary_buoyancy_pressure_differences: ndarray = np.zeros(
            (nodes_size, boundary_conditions_size)
        )
        # Go through each flow path
        for flow_path in flow_paths:
            # TODO: Check with Francois if this effect is considered in the fan flow calculation
            if "fan" not in flow_path["connection"]["connection_type"]:
                name_from: str = flow_path["path"][0]
                name_to: str = flow_path["path"][1]
                index_from: int = flow_path["path_ids"][0]
                index_to: int = flow_path["path_ids"][1]
                # Compute pressure correction value to apply later in the matrix calculation
                node_from: Any = [
                    node for node in nodes if node.id == name_from
                ][0]
                temperature: float = (
                    space_temperatures[node_from.id]
                    if isinstance(node_from, Space)
                    else node_from.exterior_air_temperature
                )
                density_from: float = ATMOSPHERIC_AIR_PRESSURE / (
                    RS_AIR
                    * UNIT_CONVERTER.convert(
                        value=temperature,
                        unit_from=Units.DEGREE_CELSIUS,
                        unit_to=Units.KELVIN,
                    )
                )
                node_to: Any = [node for node in nodes if node.id == name_to][0]
                temperature: float = (
                    space_temperatures[node_to.id]
                    if isinstance(node_to, Space)
                    else node_to.exterior_air_temperature
                )
                density_to: float = ATMOSPHERIC_AIR_PRESSURE / (
                    RS_AIR
                    * UNIT_CONVERTER.convert(
                        value=temperature,
                        unit_from=Units.DEGREE_CELSIUS,
                        unit_to=Units.KELVIN,
                    )
                )
                # Add buoyancy term to pressure flow
                pressure_difference: float = (
                    -(density_from - density_to)
                    * GRAVITATIONAL_ACCELERATION
                    * flow_path["z"]
                )
                # Fill in the matrices with pressure_difference
                # This is in the CCa matrix with system nodes
                if flow_path["flow_matrix"] == "FFa":
                    system_buoyancy_pressure_differences[
                        index_from, index_to
                    ] = -pressure_difference
                    system_buoyancy_pressure_differences[
                        index_to, index_from
                    ] = pressure_difference
                else:
                    system_and_boundary_buoyancy_pressure_differences[
                        index_from, index_to
                    ] = pressure_difference * flow_path["flow_sign"]
        buoyancy_correction: ndarray = np.sum(
            system_buoyancy_pressure_differences
            * relaxation_space_flow_resistance_nodes,
            axis=1,
        ) + np.sum(
            system_and_boundary_buoyancy_pressure_differences
            * relaxation_boundary_and_space_flow_resistance_nodes,
            axis=1,
        )
        buoyancy_correction = np.reshape(buoyancy_correction, (nodes_size, 1))
        pressures: ndarray = np.dot(
            -inv(system_pressure_matrix),
            np.dot(control_pressure_matrix, boundary_pressures)
            - buoyancy_correction
            + np.dot(imposed_flow_rates, boundary_flows),
        )
        flow_rates: ndarray = (
            pressures * relaxation_space_flow_resistance_nodes
            - np.reshape(pressures, (1, nodes_size))
            * relaxation_space_flow_resistance_nodes
            + system_buoyancy_pressure_differences
            * relaxation_space_flow_resistance_nodes
        )
        # flow_rate = flow_1 + flow_2 + flow_3
        # flow_1: Entering air flow due to pressure difference between nodes, via connections (openings etc.)
        # flow_2: Leaving air flow due to pressure difference between nodes, via connections (openings etc.)
        # flow_3: Air flow due to pressure correction of connection heights
        boundary_condition_flow_rates: ndarray = (
            pressures * relaxation_boundary_and_space_flow_resistance_nodes
            - np.reshape(boundary_pressures, (1, boundary_conditions_size))
            * relaxation_boundary_and_space_flow_resistance_nodes
            + system_and_boundary_buoyancy_pressure_differences
            * relaxation_boundary_and_space_flow_resistance_nodes
            + np.reshape(boundary_flows, (1, boundary_conditions_size))
            * imposed_flow_rates
        )
        # flowrate = flow1 + flow2 + flow3
        # flow1 : entering air flow due to pressure difference between nodes and boundary nodes via connections (openings etc.)
        # flow1 : leaving air flow due to pressure difference between nodes and boundary nodes via connections (openings etc.)
        # flow3 : air flow due to pressure correction of connection heights
        return pressures, flow_rates, boundary_condition_flow_rates
    # Solve pressure system
    pressures: ndarray = np.dot(
        -inv(system_pressure_matrix),
        np.dot(control_pressure_matrix, boundary_pressures)
        + np.dot(imposed_flow_rates, boundary_flows),
    )
    # Compute flow rates
    flow_rates: ndarray = (
        pressures * relaxation_space_flow_resistance_nodes
        - np.reshape(pressures, (1, nodes_size))
        * relaxation_space_flow_resistance_nodes
    )
    boundary_condition_flow_rates: ndarray = (
        pressures * relaxation_boundary_and_space_flow_resistance_nodes
        - np.reshape(boundary_pressures, (1, boundary_conditions_size))
        * relaxation_boundary_and_space_flow_resistance_nodes
        + np.reshape(boundary_flows, (1, boundary_conditions_size))
        * imposed_flow_rates
    )
    return pressures, flow_rates, boundary_condition_flow_rates
