"""
Helper functions for the ThermalBuilding class.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy import eye, ndarray
from scipy.linalg import expm, inv

from colibri.interfaces import ElementObject
from colibri.modules.modules_constants import CP_AIR, DENSITY_AIR
from colibri.project_objects import Boundary, Space

epsilon: float = 1e-15


def estimate_convective_heat_coefficient(
    element_type: str,
    tilt: int,
    to_exterior: bool = False,
    mode: str = "heating",
) -> float:
    """Compute the standard convective heat exchange coefficient [W/(m².K)]
       - tilt = 0: floor is side_1, ceiling side_2
       - tilt = 180: floor is side_2, ceiling side_1

    Parameters
    ----------
    element_type : str
        Type of the element/object
    tilt : int
        Tilt of the element/object
    to_exterior : bool = False
        Is it next to the exterior
    mode : str = "heating"
        Operating mode

    Returns
    -------
    h_conv : float
        Convective heat exchange coefficient [W/(m².K)]

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Standard convective heat exchange coefficients [W/(m².K)]
    # tilt = 0: floor is side_1, ceiling side_2
    # tilt = 180: floor is side_2, ceiling side_1
    h_conv_values: Dict[str, Dict[str, float]] = {
        "0": {"heating": 2.0, "cooling": 1.0, "freefloat": 1.5},
        "180": {"heating": 1.0, "cooling": 2.0, "freefloat": 1.5},
        "90": {"heating": 3.0, "cooling": 3.0, "freefloat": 3.0},
    }
    # For exterior, convective heat exchange coefficient (h_conv)
    # set to 15.0 [W/(m².K)]
    h_conv: float = 15.0
    if (tilt != 0) & (tilt != 180):
        tilt = 90
    if (to_exterior is False) and (element_type == "window"):
        h_conv = 3.0
    # Opaque
    if (to_exterior is False) and (element_type == "window"):
        h_conv = h_conv_values[str(tilt)][mode]
    return h_conv


def estimate_radiative_heat_coefficient(
    emissivity: float,
    temperature_surface: float,
    temperature_client: float,
) -> float:
    """Compute the radiative heat exchange coefficient [W/(m².K)]

    Parameters
    ----------
    emissivity : float
        Emissivity
    temperature_surface : float
        Temperature of the surface [°C]
    temperature_client : float
        Temperature of the client [°C]

    Returns
    -------
    h_rad : float
        Radiative heat exchange coefficient [W/(m².K)]

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Estimate linear radiant heat transfer coefficient
    temperature_surface += 273.15
    temperature_client += 273.15
    if temperature_surface == temperature_client:
        temperature_client += 1e-3
    h_rad: float = (
        5.667e-8
        * emissivity
        * (temperature_surface**4 - temperature_client**4)
        / (temperature_surface - temperature_client)
    )
    return h_rad


def create_elements_indices(spaces: List[Space]) -> Dict[str, int]:
    """Create an index for each element (in the matrix), which creates a map
       between IDs and rows' index


    Parameters
    ----------
    spaces : List[Space]
        List of spaces

    Returns
    -------
    elements_indices : Dict[str, int]:
        Index for each element (in the matrix)

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """

    boundaries: List[Boundary] = [
        boundary for space in spaces for boundary in space.boundaries
    ]
    windows: List[ElementObject] = [
        boundary_object
        for boundary in boundaries
        for boundary_object in boundary.object_collection
        if boundary_object.__class__.__name__ == "Window"
    ]
    elements_indices: Dict[str, int] = dict()
    node_number: int = 0
    for boundary in boundaries:
        number_of_nodes: int = len(boundary.thermal_masses)
        for node in range(number_of_nodes):
            elements_indices[boundary.label + "__node_nb_" + str(node)] = (
                node_number
            )
            node_number += 1
    for window in windows:
        elements_indices[window.label + "__ext"] = node_number
        node_number += 1
        elements_indices[window.label + "__int"] = node_number
        node_number += 1
    # Mean radiant nodes
    for space in spaces:
        elements_indices[space.label + "__mr"] = node_number
        node_number += 1
    # Air nodes
    for space in spaces:
        elements_indices[space.label + "__air"] = node_number
        node_number += 1
    return elements_indices


def generate_euler_exponential_system_and_control_matrices(
    system_matrix: ndarray,
    control_matrix: ndarray,
    time_step: int,
    label: Optional[str] = None,
) -> Tuple[ndarray, ndarray]:
    """Compute the matrix exponential of the system and control matrices (A and B):
       - system_matrix_exponential: Ad = exp(At)
       - control_matrix_exponential: Ad = exp(At)B

    Parameters
    ----------
    system_matrix : ndarray
        System matrix (A)
    control_matrix : ndarray
        Control matrix (B)
    time_step : int
        Time step (Δt)
    label : Optional[str] = None
        Label associated with the system and control matrices (A and B)

    Returns
    -------
    Tuple[ndarray, ndarray]
       - system_matrix_exponential: Ad = exp(At)
       - control_matrix_exponential: Ad = exp(At)B

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    total_number_of_nodes: int = np.shape(system_matrix)[0]
    try:
        system_matrix_exponential: ndarray = expm(system_matrix * time_step)
    except Exception:
        raise ValueError(
            f"Object '{label}' exponential A matrix cannot be computed."
        )
    try:
        control_matrix_exponential = (
            inv(system_matrix)
            .dot(system_matrix_exponential - eye(total_number_of_nodes))
            .dot(control_matrix)
        )
    except Exception:
        raise ValueError(f"Object '{label}' exponential A matrix is singular.")
    system_matrix_exponential[np.where(system_matrix_exponential < epsilon)] = 0
    control_matrix_exponential[
        np.where(control_matrix_exponential < epsilon)
    ] = 0
    return system_matrix_exponential, control_matrix_exponential


def generate_system_and_control_matrices(
    spaces: List[Space],
) -> Tuple[
    ndarray,
    ndarray,
    Dict[str, Dict[str, int]],
    Dict[str, Dict[str, int]],
]:
    """Generate the system (A) and control (B) matrix as well as
    their state and input indices

    Parameters
    ----------
    spaces : List[Space]
        List of spaces

    Returns
    -------
    Tuple[ndarray, ndarray, ndarray, ndarray]
        - system_matrix (A)
        - control_matrix (B)
        - state_indices
        - input_indices

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    boundaries: List[Boundary] = [
        boundary for space in spaces for boundary in space.boundaries
    ]
    windows: list[ElementObject] = [
        boundary_object
        for boundary in boundaries
        for boundary_object in boundary.object_collection
        if boundary_object.__class__.__name__ == "Window"
    ]
    number_of_spaces: int = len(spaces)
    number_of_windows: int = len(windows)
    number_of_boundaries: int = len(boundaries)
    number_of_wall_layers: int = 0
    for boundary in boundaries:
        number_of_wall_layers += len(boundary.thermal_masses)
    total_number_of_nodes = (
        number_of_spaces * 2 + number_of_windows * 2 + number_of_wall_layers
    )
    state_indices = {
        "boundaries": {"start_index": 0, "n_elements": number_of_wall_layers},
        "windows": {
            "start_index": number_of_wall_layers,
            "n_elements": 2 * number_of_windows,
        },
        "spaces_mean_radiant": {
            "start_index": number_of_wall_layers + 2 * number_of_windows,
            "n_elements": number_of_spaces,
        },
        "spaces_air": {
            "start_index": number_of_wall_layers
            + 2 * number_of_windows
            + number_of_spaces,
            "n_elements": number_of_spaces,
        },
    }
    input_indices = {
        "ground_temperature": {"start_index": 0, "n_elements": 1},
        "exterior_air_temperature": {
            "start_index": 1,
            "n_elements": number_of_boundaries,
        },
        "exterior_radiant_temperature": {
            "start_index": 1 * number_of_boundaries + 1,
            "n_elements": number_of_boundaries,
        },
        "radiative_gain_boundary_external": {
            "start_index": 2 * number_of_boundaries + 1,
            "n_elements": number_of_boundaries,
        },
        "space_radiative_gain": {
            "start_index": 3 * number_of_boundaries + 1,
            "n_elements": number_of_spaces,
        },
        "space_convective_gain": {
            "start_index": 3 * number_of_boundaries + 1 + number_of_spaces,
            "n_elements": number_of_spaces,
        },
    }
    number_of_inputs: int = 1 + 4 * number_of_boundaries + number_of_spaces
    # Initialise A (system matrix) and B (control matrix) matrices
    system_matrix: ndarray = np.zeros(
        (total_number_of_nodes, total_number_of_nodes)
    )
    control_matrix: ndarray = np.zeros(
        (total_number_of_nodes, number_of_inputs)
    )
    mcp = np.zeros(total_number_of_nodes)
    # Map between elements' ID and matrix rows' index
    element_row_indices: Dict[str, int] = create_elements_indices(spaces=spaces)
    # Now fill in system (A) and control (B) matrices with known indices
    # i0_boundaries = 0
    control_matrix_flux_indexing: List[List[int]] = []
    node_number: int = 0
    for boundary_number, boundary in enumerate(boundaries):
        number_of_nodes: int = len(boundary.thermal_masses)
        for node in range(number_of_nodes):
            # side 1 and side 2
            if (node == 0) or (node == number_of_nodes - 1):
                side: str = boundary.side_1 if node == 0 else boundary.side_2
                # Fill in negative on diag(A) and positive in
                # control_matrix (B) if exterior
                if side == "exterior":
                    # Surface exchange with external air node, fill in
                    # control matrix (B) only with convective coefficients
                    h_conv: float = estimate_convective_heat_coefficient(
                        element_type="opaque",
                        tilt=boundary.tilt,
                        to_exterior=True,
                    )
                    # Index for air temperature of each boundary is equal
                    # to the number of boundary
                    index_to_air: int = (
                        input_indices["exterior_air_temperature"]["start_index"]
                        + boundary_number
                    )
                    control_matrix[node_number, index_to_air] += (
                        h_conv * boundary.area
                    )
                    # Long wave radiation coefficients
                    # Radiant coefficient at external surface towards outside
                    h_rad: float = estimate_radiative_heat_coefficient(
                        emissivity=boundary.emissivities[0],
                        temperature_surface=10.0,
                        temperature_client=0.0,
                    )
                    # Index for mean radiant external temperature of each
                    # boundary is equal to the number of boundary
                    index_to_tmr: int = (
                        input_indices["exterior_radiant_temperature"][
                            "start_index"
                        ]
                        + boundary_number
                    )
                    control_matrix[node_number, index_to_tmr] += (
                        h_rad * boundary.area
                    )
                    # Flux indexing and scaling (applied at the end of
                    # this function, to allow calculation of diagonal of A)
                    # Radiative flux is in W/m², i.e. coefficient is the
                    # area of the element
                    control_matrix_flux_indexing.append(
                        [
                            node_number,
                            input_indices["radiative_gain_boundary_external"][
                                "start_index"
                            ]
                            + boundary_number,
                            boundary.area,
                        ]
                    )
                # Fill in control matrix (B) only
                elif side == "ground":
                    # 1m distance and conductivity of 2.0 W/m/K,
                    # could be made for specific ground
                    resistance_ground_1m: float = 1.0 / 2.0
                    index_ground: int = input_indices["ground_temperature"][
                        "start_index"
                    ]
                    control_matrix[node_number, index_ground] += (
                        1 / resistance_ground_1m * boundary.area
                    )
                # Fill in control matrix (B) only
                elif side == "boundary":
                    # Remark: in case of specification of "boundary",
                    # the field "exterior_air_temperature" is used,
                    # and "exterior_radiant_temperature" not connected
                    # Very small resistance to connect directly the
                    # boundary temperature
                    resistance_boundary: float = 1e-10
                    index_boundary: int = (
                        input_indices["exterior_air_temperature"]["start_index"]
                        + boundary_number
                    )
                    control_matrix[node_number, index_boundary] += (
                        1 / resistance_boundary * boundary.area
                    )
                # Internal air space, fill inside A only
                else:
                    # Search corresponding air node index
                    h_conv: float = estimate_convective_heat_coefficient(
                        element_type="opaque",
                        tilt=boundary.tilt,
                    )
                    index_to_air_node: int = list(element_row_indices).index(
                        side + "__air"
                    )
                    system_matrix[node_number, index_to_air_node] += (
                        h_conv * boundary.area
                    )
                    system_matrix[index_to_air_node, node_number] += (
                        h_conv * boundary.area
                    )
                    # Search corresponding air node index
                    h_rad: float = estimate_radiative_heat_coefficient(
                        emissivity=boundary.emissivities[0],
                        temperature_surface=20.0,
                        temperature_client=20.0,
                    )
                    index_to_tmr_node: int = list(element_row_indices).index(
                        side + "__mr"
                    )
                    system_matrix[node_number, index_to_tmr_node] += (
                        h_rad * boundary.area
                    )
                    system_matrix[index_to_tmr_node, node_number] += (
                        h_rad * boundary.area
                    )
                    # Flux indexing (applied at the end of this function,
                    # to allow calculation of diagonal of A)
                    for space_number, space in enumerate(spaces):
                        for element in space.envelope_elements:
                            if element == boundary.label:
                                radiative_share: float = (
                                    space.envelope_elements[element][
                                        "radiative_share"
                                    ]
                                )
                                # radiative_gain_boundary_external
                                control_matrix_flux_indexing.append(
                                    [
                                        node_number,
                                        input_indices["space_radiative_gain"][
                                            "start_index"
                                        ]
                                        + space_number,
                                        radiative_share,
                                    ]
                                )
                # Conduction towards next (node = 0) or previous node (node == number_of_nodes)
                if node == 0:
                    system_matrix[node_number, node_number + 1] += (
                        1 / boundary.resistances[node] * boundary.area
                    )
                if node == number_of_nodes - 1:
                    system_matrix[node_number, node_number - 1] += (
                        1 / boundary.resistances[node - 1] * boundary.area
                    )
            # Internal material nodes, only conduction
            else:
                system_matrix[node_number, node_number + 1] = (
                    1 / boundary.resistances[node] * boundary.area
                )
                system_matrix[node_number, node_number - 1] = (
                    1 / boundary.resistances[node - 1] * boundary.area
                )
            mcp[node_number] = boundary.thermal_masses[node]
            node_number += 1
    # Now node_number is the first index of windows
    for window in windows:
        # Window in this model has 2 nodes:
        # internal surface node and external surface node
        for node in range(2):
            side: str = window.side_1 if node == 0 else window.side_2
            # Fill in control matrix (B) if to exterior
            if side == "exterior":
                # Surface exchange with external air node,
                # fill in control matrix (B) only
                # Convective coefficients
                # NOTE: Perhaps values for single 6, double 4.5 and triple glazing? 3
                h_conv: float = estimate_convective_heat_coefficient(
                    element_type="window", tilt=window.tilt, to_exterior=True
                )
                # Index for air temperature of each boundary is equal to
                # the number of boundary
                index_to_air: int = (
                    input_indices["exterior_air_temperature"]["start_index"]
                    + window.boundary_number
                )
                control_matrix[node_number, index_to_air] += (
                    h_conv * window.area
                )
                # Long wave radiation coefficients
                # Radiant coefficient at external surface towards outside
                h_rad: float = estimate_radiative_heat_coefficient(
                    emissivity=window.emissivities[0],
                    temperature_surface=10.0,
                    temperature_client=0.0,
                )
                # Index for mean radiant external temperature of each boundary
                # is equal to the number of boundary
                index_to_tmr: int = (
                    input_indices["exterior_radiant_temperature"]["start_index"]
                    + window.boundary_number
                )
                control_matrix[node_number, index_to_tmr] += h_rad * window.area
                # Flux indexing (applied at the end of this function,
                # to allow calculation of diagonal of A)
                # Radiative flux is in W/m², i.e. coefficient is the area of the element
                # radiative_gain_boundary_external absorbed by window
                control_matrix_flux_indexing.append(
                    [
                        node_number,
                        input_indices["radiative_gain_boundary_external"][
                            "start_index"
                        ]
                        + window.boundary_number,
                        window.area * window.absorption,
                    ]
                )
                # TODO: solar transmission into zone
            # Internal air space, fill inside system matrix (A) only
            else:
                # Search corresponding air node index
                # Convective heat exchange coefficients
                # TODO: window h_conv depends on glazing type and
                # temperature difference, different to walls
                h_conv = estimate_convective_heat_coefficient(
                    element_type="window", tilt=window.tilt
                )
                index_to_air_node = list(element_row_indices).index(
                    side + "__air"
                )
                system_matrix[node_number, index_to_air_node] += (
                    h_conv * window.area
                )
                system_matrix[index_to_air_node, node_number] += (
                    h_conv * window.area
                )
                # long wave radiation coefficients
                h_rad: float = estimate_radiative_heat_coefficient(
                    emissivity=window.emissivities[1],
                    temperature_surface=20.0,
                    temperature_client=20.0,
                )
                index_to_tmr_node: int = list(element_row_indices).index(
                    side + "__mr"
                )
                system_matrix[node_number, index_to_tmr_node] += (
                    h_rad * window.area
                )
                system_matrix[index_to_tmr_node, node_number] += (
                    h_rad * window.area
                )
                # Flux indexing (applied at the end of this function,
                # to allow calculation of diagonal of A)
                for space_number, space in enumerate(spaces):
                    for env in space.envelope_elements:
                        if env == window.label:
                            radiative_share = space.envelope_elements[env][
                                "radiative_share"
                            ]
                            # radiative_gain_boundary_external
                            control_matrix_flux_indexing.append(
                                [
                                    node_number,
                                    input_indices["space_radiative_gain"][
                                        "start_index"
                                    ]
                                    + space_number,
                                    radiative_share,
                                ]
                            )
            # Conduction towards next (node = 0) or previous node (node == 1)
            resistance_window = 1 / window.u_value
            # TODO: correct for internal and external heat exchange coefficients !
            window_u_value: float = get_window_u_value(
                resistance_window=resistance_window,
                h_rad_ext=5.25,
                h_rad_int=5.25,
                h_conv_ext=16.37,
                h_conv_int=3.16,
            )
            if node == 0:
                system_matrix[node_number, node_number + 1] += (
                    window_u_value * window.area
                )
            if node == 1:
                system_matrix[node_number, node_number - 1] += (
                    window_u_value * window.area
                )
            mcp[node_number] = 1.0 * window.area
            node_number += 1
    # Mean radiant nodes, already filled in in boundaries and windows!
    for space in spaces:
        mcp[node_number] = space.volume * CP_AIR * DENSITY_AIR
        node_number += 1
    # Air nodes
    for space_number, space in enumerate(spaces):
        mcp[node_number] = space.volume * CP_AIR * DENSITY_AIR
        # Flux indexing (applied at the end of this function, to allow calculation of diagonal of A)
        # Convective gain to space air node
        control_matrix_flux_indexing.append(
            [
                node_number,
                input_indices["space_convective_gain"]["start_index"]
                + space_number,
                1,
            ]
        )
        node_number += 1
    # Compute diagonal of A with leaving coefficients
    for node_number in range(number_of_nodes):
        system_matrix[node_number, node_number] -= np.sum(
            system_matrix[node_number, :]
        ) + np.sum(control_matrix[node_number, :])
    # Add indexes for heat fluxes into control matrix (B)
    for flux in control_matrix_flux_indexing:
        # Connect flux by scaling factor flux[2]
        control_matrix[flux[0], flux[1]] = flux[2]
    # correct cp values (are in kJ/kg/K for the moment)
    for node_number in range(number_of_nodes):
        system_matrix[node_number, :] /= mcp[node_number]
        control_matrix[node_number, :] /= mcp[node_number]
    return system_matrix, control_matrix, state_indices, input_indices


def get_states_from_index(
    states: ndarray, index_states: Dict[str, Dict[str, int]], label: str
) -> ndarray:
    """Get the states from the index

    Parameters
    ----------
    states : ndarray
        Array of states
    index_states : Dict[str, Dict[str, int]]
        Starting and length of the states' indices
    label : str
        Label of the element whose states must be retrieved

    Returns
    -------
    ndarray
        States of the element

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    state_indices: Dict[str, int] = index_states[label]
    start_index: int = state_indices["start_index"]
    end_index: int = state_indices["start_index"] + state_indices["n_elements"]
    return states[start_index:end_index]


def get_window_u_value(
    resistance_window: float,
    h_rad_ext: float,
    h_rad_int: float,
    h_conv_ext: float = 8.0,
    h_conv_int: float = 2.4,
) -> float:
    """Get the window U value

    Parameters
    ----------
    resistance_window : float
        Resistance of the window
    h_rad_ext : float
        Radiative heat transfer coefficient with the exterior
    h_rad_int : float
        Radiative heat transfer coefficient with the interior
    h_conv_ext : float = 8.0
        Convective heat transfer coefficient with the exterior
    h_conv_int : float = 2.4
        Convective heat transfer coefficient with the interior

    Returns
    -------
    window_u_value : float
        Window intrinsic U value

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Window parameters (using same hrad and hconv coefficients as walls)
    # Estimate intrinsic U value of envelope element.
    # Intrinsic means from one surface node to the other one.
    try:
        r_window_int: float = (
            resistance_window
            - 1.0 / (h_conv_ext + h_rad_ext)
            - 1.0 / (h_conv_int + h_rad_int)
        )
        window_u_value: float = 1.0 / r_window_int
    except (TypeError, ZeroDivisionError):
        window_u_value: float = 0.0
    # In case the U-value has been set to high, not coherent with heat exchange coefficients
    if window_u_value <= 0:
        window_u_value = 0.01
    return window_u_value


def run_state_space(
    system_matrix: ndarray,
    control_matrix: ndarray,
    states: ndarray,
    input_signals: ndarray,
) -> ndarray:
    """Compute the state space (Ax + Bu)

    Parameters
    ----------
    system_matrix : ndarray
        System matrix (A)
    control_matrix : ndarray
        Control matrix (B)
    states : ndarray
        States (x)
    input_signals : ndarray
        Input signals (u)

    Returns
    -------
    ndarray
        State space (Ax + Bu)

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    return np.dot(system_matrix, states) + np.dot(control_matrix, input_signals)


def set_input_signals_from_index(
    input_signals: ndarray,
    input_signals_indices: Dict[str, Dict[str, int]],
    label: str,
    value_to_set: float,
    add: bool = False,
) -> None:
    """Set the input signals at the specified indices with the given value

    Parameters
    ----------
    input_signals : ndarray
        Input signal (U from Ax + Bu)
    input_signals_indices : Dict[str, Dict[str, int]]
        Indices for the input signals
    label: str
        Label to get the specific indices
    value_to_set: float
        Value to be set or added
    add: bool = False
        Add if add is set to True, set otherwise

    Returns
    -------
    None

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    start_index: int = input_signals_indices[label]["start_index"]
    end_index: int = start_index + input_signals_indices[label]["n_elements"]
    if add:
        input_signals[start_index:end_index] += value_to_set
    else:
        input_signals[start_index:end_index] = value_to_set


def set_boundary_discretization_properties(boundary: Boundary) -> None:
    """Generate the boundary's resistances, thermal conductances and thermal masses

    Parameters
    ----------
    boundary : Boundary
        Boundary

    Returns
    -------
    None
    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Generate the resistances between all nodes in all layers
    # of a boundary (wall, ceiling, floor)
    # Load properties
    thicknesses: float = boundary.thicknesses
    thermal_conductivities: float = boundary.thermal_conductivities
    densities: float = boundary.densities
    specific_heats: float = boundary.specific_heats
    discretization_layers: List[int] = (
        boundary.discretization_layers
    )  # Number of discretization layers
    # Create discretization variables
    number_of_nodes: int = (
        sum(discretization_layers) + 2
    )  # Total number of nodes (nodes + 2 surface nodes)
    x: ndarray = np.zeros(
        number_of_nodes
    )  # x position of nodes starting from side_1 = 0. Side_2 = total thicknesses
    resistances: ndarray = np.zeros(number_of_nodes - 1)
    thermal_masses: ndarray = np.zeros(number_of_nodes)
    node_number: int = 0  # Counter of nodes
    # First surface node at side_1
    x[node_number] = 0.0
    # Very thin cover layer at surface, no mass
    thermal_masses[node_number] = (
        thicknesses[0]
        / (discretization_layers[0] + 1)
        / 100.0
        * densities[0]
        * specific_heats[0]
    )
    node_number += 1
    # Go through each intermediate nodes that are not at the surface
    for layer_index, thickness in enumerate(thicknesses):
        for discretization_index in range(discretization_layers[layer_index]):
            # Internal interface between 2 different layers
            if (layer_index > 0) and (discretization_index == 0):
                x[node_number] = (
                    x[node_number - 1]
                    + thicknesses[layer_index - 1]
                    / (discretization_layers[layer_index - 1] + 1)
                    + thickness / (discretization_layers[layer_index] + 1)
                )
                resistances[node_number - 1] = round(
                    thicknesses[layer_index - 1]
                    / (discretization_layers[layer_index - 1] + 1)
                    / thermal_conductivities[layer_index - 1]
                    + thickness
                    / (discretization_layers[layer_index] + 1)
                    / thermal_conductivities[layer_index],
                    3,
                )
                thermal_masses[node_number] = (
                    thicknesses[layer_index - 1]
                    / (discretization_layers[layer_index - 1] + 1)
                    * densities[layer_index - 1]
                    * specific_heats[layer_index - 1]
                    + thickness
                    / (discretization_layers[layer_index] + 1)
                    * densities[layer_index]
                    * specific_heats[layer_index]
                )
            # All other nodes
            else:
                x[node_number] = x[node_number - 1] + thicknesses[
                    layer_index
                ] / (discretization_layers[layer_index] + 1)
                resistances[node_number - 1] = round(
                    thickness
                    / (discretization_layers[layer_index] + 1)
                    / thermal_conductivities[layer_index],
                    3,
                )
                thermal_masses[node_number] = (
                    thickness
                    / (discretization_layers[layer_index] + 1)
                    * densities[layer_index]
                    * specific_heats[layer_index]
                )
            node_number += 1
    # Last node towards side_2
    x[node_number] = sum(thicknesses)
    resistances[node_number - 1] = round(
        thickness
        / (discretization_layers[layer_index] + 1)
        / thermal_conductivities[layer_index],
        3,
    )
    thermal_masses[node_number] = (
        thickness
        / (discretization_layers[layer_index] + 1)
        / 100.0
        * densities[layer_index]
        * specific_heats[layer_index]
    )
    # Compute distance between nodes
    boundary.resistances = resistances
    boundary.u_value = round(1.0 / np.sum(resistances), 3)
    boundary.thermal_masses = thermal_masses * boundary.area


def set_radiative_shares(spaces: List[Space]) -> None:
    """Set the radiative shares in each space

    Parameters
    ----------
    spaces : List[Space]
        List of spaces

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the sum of all the radiative shares is not equal to 1

    Examples
    --------
    >>> None
    """
    for space in spaces:
        space.envelope_area = 0.0
        space.envelope_elements = dict()
        for boundary in space.boundaries:
            # TODO: c'est pas beau et peut planter si on ne nomme pas pareil
            if ("floor" in boundary.label) or ("plancher" in boundary.label):
                type_of_element: str = "floor"
            else:
                type_of_element: str = "other"
            # If it is an internal wall in a space, both sides are accounted for (very simplified)
            # This side is in contact with the current space
            if boundary.side_1 == space.label:
                if type_of_element != "floor":
                    space.envelope_area += boundary.area
                if boundary.side_2 == "exterior":
                    u_value = boundary.u_value
                else:
                    u_value = 0.0
                space.envelope_elements[boundary.label] = {
                    "type": type_of_element,
                    "area": boundary.area,
                    "side": "side_1",
                    "u_value": u_value,
                }
            if (
                boundary.side_2 == space.label
            ):  # this side is in contact with the current space
                if type_of_element != "floor":
                    space.envelope_area += boundary.area
                if boundary.side_1 == "exterior":
                    u_value = boundary.u_value
                else:
                    u_value = 0.0
                space.envelope_elements[boundary.label] = {
                    "type": type_of_element,
                    "area": boundary.area,
                    "side": "side_2",
                    "u_value": u_value,
                }
        # Look which boundary is in contact with the current space
        windows: List[ElementObject] = [
            boundary_object
            for boundary in space.boundaries
            for boundary_object in boundary.object_collection
            if boundary_object.__class__.__name__ == "Window"
        ]
        for window in windows:
            # If it is an internal wall in a space, both sides are accounted for (very simplified)
            # This side is in contact with the current space
            if window.side_1 == space.label:
                space.envelope_area += window.area
                space.envelope_elements[window.label] = {
                    "type": "window",
                    "area": window.area,
                    "side": "side_1",
                    "boundary_name": window.boundary_id,
                    "transmittance": window.transmittance,
                    "u_value": window.u_value,
                }
            # this side is in contact with the current space
            if window.side_2 == space.label:
                space.envelope_area += window.area
                space.envelope_elements[window.label] = {
                    "type": "window",
                    "area": window.area,
                    "side": "side_1",
                    "boundary_name": window.boundary_id,
                    "transmittance": window.transmittance,
                    "u_value": window.u_value,
                }
    # No go through again and associate radiative distribution shares
    floor_rad_share: float = 0.642  # bestest value ...
    for space in spaces:
        checker = 0.0
        for element in space.envelope_elements:
            if space.envelope_elements[element]["type"] == "floor":
                rad_share: float = floor_rad_share
            else:
                rad_share: float = round(
                    (
                        space.envelope_elements[element]["area"]
                        / space.envelope_area
                        * (1 - floor_rad_share)
                    ),
                    3,
                )
            space.envelope_elements[element]["radiative_share"] = rad_share
            checker += rad_share
        if np.abs(checker - 1) > 1e-2:
            raise ValueError(
                f"Radiative share calculation is wrong. "
                f"The sum of all shares must be equal to 1, but is {checker}"
            )


def set_u_values(spaces: List[Space]) -> None:
    """Set the u values in each space

    Parameters
    ----------
    spaces : List[Space]
        List of spaces

    Returns
    -------
    None

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    u_wall: float = 0.0
    wall_area: float = 0.0
    u_window: float = 0.0
    window_area: float = 0.0
    for space in spaces:
        for element_name in space.envelope_elements:
            element: Dict[str, Any] = space.envelope_elements[element_name]
            if element["type"] != "window":
                u_wall += element["u_value"] * element["area"]
                wall_area += element["area"]
            else:
                u_window += element["u_value"] * element["area"]
                window_area += element["area"]
        if wall_area > 0:
            u_wall /= wall_area
        if window_area > 0:
            u_window /= window_area
        space.u_wall = round(u_wall, 3)
        space.u_window = round(u_window, 3)
        space.wall_area = round(wall_area, 2)
        space.window_area = round(window_area, 2)
