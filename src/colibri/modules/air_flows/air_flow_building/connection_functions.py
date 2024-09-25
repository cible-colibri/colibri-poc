"""
Function to compute the pressure loss ΔP for mechanical fans based on delta pressure law, which is the characteristic fan curve.
"""

from typing import Tuple


def compute_pressure_loss_for_mechanical_fans(
    flow_rate: float = 45.0,
    delta_pressure_law: Tuple[
        Tuple[float, float, float], Tuple[float, float, float]
    ] = [[0, 45, 100], [80, 80, 0]],
):
    """Compute the pressure loss ΔP for mechanical fans based on
       delta pressure law, which is the characteristic fan curve
       ΔP = f(flow_rate):
        - delta_pressure_law[0]: input with flow rates passing the fan
        - delta_pressure_law[1]: output with pressure gains from the fan

    Parameters
    ----------
    flow_rate : float = 45.0
        Flow rate of the mechanical fan [m³/h]
    delta_pressure_law : Tuple[float, float, float], Tuple[float, float, float] = [[0, 45, 100], [80, 80, 0]]
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
