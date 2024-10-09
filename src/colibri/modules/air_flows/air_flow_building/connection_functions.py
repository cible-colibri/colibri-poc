"""
Function to compute the pressure loss ΔP for mechanical fans based on delta pressure law, which is the characteristic fan curve.
"""

from typing import List

import numpy as np


def compute_door_back_pressure_coefficient(
    section: float = 2.0,
    discharge_coefficient: float = 0.6,
    opening: float = 1.0,
) -> float:
    """Compute the door's back pressure coefficient (kb)

    Parameters
    ----------
    section : float = 2.0
        Section of the door
    discharge_coefficient : float = 0.6
        Discharge coefficient (kd)
    opening : float = 1.0
        Opening

    Returns
    -------
    kb : float
        Back pressure coefficient

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Back pressure coefficient (kb)
    kb: float = discharge_coefficient * section * opening * 2**0.5
    return kb


def compute_grille_back_pressure_coefficient(
    dp_0: float = 20.0,
    rho_0: float = 1.2,
    flow_0: float = 0.5,
    n: float = 0.5,
    opening: float = 1.0,
) -> float:
    """Compute the door's back pressure coefficient (kb)

    Parameters
    ----------
    section : float = 2.0
        Section of the door
    discharge_coefficient : float = 0.6
        Discharge coefficient (kd)
    opening : float = 1.0
        Opening

    Returns
    -------
    kb : float
        Back pressure coefficient

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Back pressure coefficient
    kb = opening * flow_0 / 3600.0 / dp_0**n / rho_0 ** (n - 1)
    return kb


def compute_pressure_loss_for_mechanical_fans(
    flow_rate: float = 45.0,
    delta_pressure_law: List[List[float]] = [[0, 45, 100], [80, 80, 0]],
) -> float:
    """Compute the pressure loss ΔP for mechanical fans based on
       delta pressure law, which is the characteristic fan curve
       ΔP = f(flow_rate):
        - delta_pressure_law[0]: input with flow rates passing the fan
        - delta_pressure_law[1]: output with pressure gains from the fan

    Parameters
    ----------
    flow_rate : float = 45.0
        Flow rate of the mechanical fan [m³/h]
    delta_pressure_law : List[List[float]] = [[0, 45, 100], [80, 80, 0]]
        Characteristic fan curve ΔP = f(flow_rate)

    Returns
    -------
    pressure_loss : float
        Pressure loss ΔP from interpolation between data points

    Raises
    ------
    None

    Notes
    -----
    ΔP  = -interpolate_function(flowrate, dplaw) does not work for the moment!

    Examples
    --------
    >>> None
    """
    flow_rate = max(0.0, flow_rate)
    for index, value in enumerate(delta_pressure_law[0]):
        if delta_pressure_law[0][index] <= flow_rate:
            law_index = index
    pressure_loss: float = -(
        delta_pressure_law[1][law_index]
        + (flow_rate - delta_pressure_law[0][law_index])
        / (
            delta_pressure_law[0][law_index + 1]
            - delta_pressure_law[0][law_index]
        )
        * (
            delta_pressure_law[1][law_index + 1]
            - delta_pressure_law[1][law_index]
        )
    )
    return pressure_loss


def compute_dtu_duct_pressure_loss(
    flow_rate: float = 45.0,
    density: float = 1.2,
    section: float = 0.005,
    hydraulic_diameter: float = 0.08,
    length: float = 1.0,
    friction_factor: float = 3.0e6,
    pressure_drop_coefficients: List[float] = [0.0, 0.0],
    computation_mode: str = "pressure",
) -> float:
    """Compute the DTU duct pressure loss ΔP
    Parameters
    ----------
    flow_rate : float = 45.0
        Flow rate inside the duct [m³/h]
    density: float = 1.2
        Volumetric density ρ of the fluid inside the duct [kg/m³]
    section: float = 0.005
        Section of the duct
    hydraulic_diameter: float = 0.08
        Hydraulic diameter of the duct [m]
    length : float = 1.0
        Length of the duct [m]
    friction_factor : float = 3.0e6
         Dimensionless friction factor
    pressure_drop_coefficients : List[float] = [0.0, 0.0]
         Dimensionless loss coefficient ζ
         (positive flow direction and negative flow direction)
    computation_mode : str = "pressure"
        Computation mode ("pressure" or "c_lin")

    Returns
    -------
    pressure_loss : float
        Pressure loss ΔP

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    if flow_rate == 0:
        return 0
    singular_loss_coefficient = (
        pressure_drop_coefficients[0]
        if flow_rate > 0
        else -pressure_drop_coefficients[1]
    )
    c1 = friction_factor * length / (1000 * hydraulic_diameter) ** 5
    c2 = singular_loss_coefficient * 0.5 * density * (1 / 3600 / section) ** 2
    if computation_mode == "pressure":
        return np.sign(flow_rate) * (
            c1 * np.abs(flow_rate) ** 1.9 + c2 * flow_rate**2
        )
    # convert to quadratic function for matrix air flow calculation
    if computation_mode == "c_lin":
        return 1 / (c1 + c2)
    raise ValueError(
        f"Unknown '{computation_mode}' computation mode " f"for the duct model."
    )
