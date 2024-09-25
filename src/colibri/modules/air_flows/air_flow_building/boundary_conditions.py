"""
Function to compute the temperature/pressure boundary conditions.
"""

from typing import List, Tuple

import numpy as np
from pandas import Series

from colibri.project_objects import BoundaryCondition


def compute_boundary_conditions(
    exterior_air_temperatures: Series,
    boundary_conditions: List[BoundaryCondition],
    number_of_time_steps: int,
    dynamic_test: int,
    apply_disturbance: Tuple[int, int],
) -> None:
    """Compute the temperature/pressure boundary conditions

    Parameters
    ----------
    exterior_air_temperatures : Series
        Exterior air temperatures
    boundary_conditions : List[BoundaryCondition]
        Boundary conditions
    number_of_time_steps : int
        Number of time steps
    dynamic_test : int
        TODO: ?
    apply_disturbance : Tuple[int, int]
        TODO: ?

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
    time_steps: np.ndarray = np.arange(number_of_time_steps)
    number_of_boundary_conditions: int = 0
    for boundary_condition in boundary_conditions:
        number_of_boundary_conditions += 1
        pressures: np.ndarray = (
            -80.0
            + dynamic_test
            * (np.cos(time_steps * np.pi / 120 * number_of_boundary_conditions))
            * 50.0
        )
        if apply_disturbance[1] > 0:
            pressures[
                (np.mod(time_steps, apply_disturbance[1]) == 0)
                & (time_steps != 0)
            ] += apply_disturbance[0] * number_of_boundary_conditions
        boundary_condition.pressures = pressures
        boundary_condition.exterior_air_temperatures = exterior_air_temperatures
