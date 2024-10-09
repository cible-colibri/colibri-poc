"""
Helper control functions for the ThermalBuilding class.
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from numpy import ndarray

from colibri.modules.thermal_spaces.detailed_building.rycj import (
    get_states_from_index,
    run_state_space,
    set_input_signals_from_index,
)


def get_operation_mode(
    indoor_temperatures: ndarray,
    outdoor_temperature: float,
    heating_setpoints: ndarray,
    cooling_setpoints: ndarray,
    operating_modes: List[str],
) -> Tuple[List[str], ndarray]:
    """Get the states from the index

    Parameters
    ----------
    indoor_temperatures: ndarray
        Space temperature
    outdoor_temperature : float
        Outdoor air temperature
    heating_setpoints : ndarray
        Heating setpoint for each space
    cooling_setpoints : ndarray
        Cooling setpoint for each space
    operating_modes : List[str]
        Mode for each space

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
    number_of_spaces: int = len(indoor_temperatures)
    space_operating_modes: List[str] = [None] * number_of_spaces
    temperature_setpoints: ndarray = np.zeros(number_of_spaces)
    # TODO: Changer en faisant des mask sur les array beaucoup plus rapide et efficace
    #      transformer le heating/cooling en int
    for index, heating_setpoint in enumerate(heating_setpoints):
        threshold: float = (heating_setpoint + cooling_setpoints[index]) / 2.0
        reference_temperature = indoor_temperatures[index]
        if (reference_temperature <= threshold) and (
            outdoor_temperature < 15.0
        ):
            if "heating" in operating_modes:
                space_operating_modes[index] = "heating"
                temperature_setpoints[index] = heating_setpoint
            else:
                space_operating_modes[index] = "free_float"
                temperature_setpoints[index] = np.nan
        elif (reference_temperature > threshold) and (
            outdoor_temperature > 16.0
        ):
            if "cooling" in operating_modes:
                space_operating_modes[index] = "cooling"
                temperature_setpoints[index] = cooling_setpoints[index]
            else:
                space_operating_modes[index] = "free_float"
                temperature_setpoints[index] = np.nan
        else:
            space_operating_modes[index] = "free_float"
            temperature_setpoints[index] = np.nan
    return space_operating_modes, temperature_setpoints


def space_temperature_control_simple(
    operating_modes: List[str],
    temperature_setpoints: ndarray,
    system_matrix: ndarray,
    control_matrix: ndarray,
    states_last: ndarray,
    input_signals: ndarray,
    index_states: Dict[str, Dict[str, int]],
    index_inputs: Dict[str, Dict[str, int]],
    radiative_share_hvac: ndarray,
    max_heating_power: ndarray,
    max_cooling_power: ndarray,
    ventilation_gain_coefficients: ndarray,
    efficiency_heat_recovery: float,
    convective_internal_gains: ndarray,
    radiative_internal_gains: ndarray,
    internal_temperatures: Dict[str, float],
    flows: List[List[Any]],
):
    space_air_temperatures: ndarray = get_states_from_index(
        states=states_last,
        index_states=index_states,
        label="spaces_air",
    )
    number_of_spaces: int = len(space_air_temperatures)
    estimated_zone_temperatures: ndarray = np.zeros((number_of_spaces, 2))
    estimated_thermal_outputs: ndarray = np.zeros(number_of_spaces)
    phi_inj: ndarray = np.zeros((number_of_spaces, 2))
    outdoor_temperature: float = input_signals[1]
    if (not flows) or (flows == 0):
        ventilation_gains: ndarray = (
            outdoor_temperature - space_air_temperatures
        ) * ventilation_gain_coefficients
    else:
        ventilation_gains: ndarray = compute_ventilation_losses(
            flows=flows,
            air_temperatures=internal_temperatures,
            outdoor_temperature=outdoor_temperature,
            efficiency_heat_recovery=efficiency_heat_recovery,
        )
    for space_index, operating_mode in enumerate(operating_modes):
        # Set minimum and maximum heating or cooling power
        if operating_mode == "heating":
            phi_inj[space_index, :] = [0.0, max_heating_power[space_index]]
        elif operating_mode == "cooling":
            phi_inj[space_index, :] = [-max_cooling_power[space_index], 0.0]
        else:
            phi_inj[space_index, :] = [0.0, 0.0]
    if np.sum(np.abs(phi_inj)) > 1e-1:
        # Minimum and maximum power
        for n in range(2):
            # Define convective and radiative heating/cooling share
            thermal_output_radiative_max = phi_inj[:, n] * radiative_share_hvac
            thermal_output_convective_max = phi_inj[:, n] * (
                1 - radiative_share_hvac
            )
            # Apply current heat flux sent from solver
            convective_gains: float = (
                thermal_output_convective_max
                + ventilation_gains
                + convective_internal_gains
            )
            set_input_signals_from_index(
                input_signals=input_signals,
                input_signals_indices=index_inputs,
                label="space_convective_gain",
                value_to_set=convective_gains,
            )
            radiative_gains: float = (
                thermal_output_radiative_max + radiative_internal_gains
            )
            set_input_signals_from_index(
                input_signals=input_signals,
                input_signals_indices=index_inputs,
                label="space_radiative_gain",
                value_to_set=radiative_gains,
            )
            # Compute building states
            states: ndarray = run_state_space(
                system_matrix=system_matrix,
                control_matrix=control_matrix,
                states=states_last,
                input_signals=input_signals,
            )
            estimated_zone_temperatures[:, n] = get_states_from_index(
                states=states, index_states=index_states, label="spaces_air"
            )
        # Obtain ideal control values (temperature and power) from linear interpolation
        for index, temperature_setpoint in enumerate(temperature_setpoints):
            delta_estimated: float = (
                estimated_zone_temperatures[index, 1]
                - estimated_zone_temperatures[index, 0]
            )
            delta_threshold: float = 0.001
            if np.sum(abs(delta_estimated)) < delta_threshold:
                estimated_thermal_outputs[index] = (
                    phi_inj[index, 1] + phi_inj[index, 0]
                ) / 2.0
            elif operating_modes[index] == "heating":
                estimated_thermal_outputs[index] = min(
                    max(
                        (
                            temperature_setpoints[index]
                            - estimated_zone_temperatures[index, 0]
                        )
                        / delta_estimated
                        * (phi_inj[index, 1] - phi_inj[index, 0]),
                        phi_inj[index, 0],
                    ),
                    phi_inj[index, 1],
                )
            elif operating_modes[index] == "cooling":
                estimated_thermal_outputs[index] = max(
                    min(
                        (
                            estimated_zone_temperatures[index, 1]
                            - temperature_setpoints[index]
                        )
                        / delta_estimated
                        * (phi_inj[index, 0] - phi_inj[index, 1]),
                        phi_inj[index, 1],
                    ),
                    phi_inj[index, 0],
                )
            else:
                estimated_thermal_outputs[index] = 0.0
    return estimated_thermal_outputs


def compute_ventilation_losses(
    flows: List[List[Any]],
    air_temperatures: Dict[str, float],
    outdoor_temperature: float,
    efficiency_heat_recovery: float,
) -> ndarray:
    """Compute the ventilation losses

    Parameters
    ----------
    flows: List[List[Any]]
        Flow rates
    air_temperatures: Dict[str, float]
        Air temperature per zone
    outdoor_temperature: float
        Outdoor air temperature
    efficiency_heat_recovery:
        Efficiency heat recovery of the ventilation

    Returns
    -------
    ventilation_losses : ndarray
        Ventilation losses

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    ventilation_losses = np.zeros(len(air_temperatures))
    for index, (space_id, air_temperature_temperature) in enumerate(
        air_temperatures.items()
    ):
        for flow in flows:
            flow_condition_name: str = flow[0]
            flow_space_id: str = flow[1]
            flow_value: float = flow[2]
            # Flow rate which gets in
            if (flow_space_id == space_id) & (flow_value > 0):
                ventilation_gain_coefficient = (
                    1006.0 * 1.2 * flow_value / 3600.0
                )
                # flow comes from outside
                if "BC" in flow_condition_name:
                    ventilation_losses[index] = (
                        (outdoor_temperature - air_temperature_temperature)
                        * ventilation_gain_coefficient
                        * (1.0 - efficiency_heat_recovery)
                    )
                else:
                    ventilation_losses[index] = (
                        air_temperatures[flow_condition_name]
                        - air_temperature_temperature
                    ) * ventilation_gain_coefficient
    return ventilation_losses
