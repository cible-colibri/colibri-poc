import numpy as np
from scipy import optimize
from models.thermal.vnat.thermal_model.RyCj import runStateSpace, set_U_from_index, get_states_from_index


def calculate_ventilation_losses(flow_array, air_temperature_temperatures_dict, outdoor_temperature, efficiency_heat_recovery, ventilation_specific_flow_array):
    ventilation_losses = np.zeros(len(air_temperature_temperatures_dict))
    for i, space in enumerate(air_temperature_temperatures_dict):
        for flow_path in flow_array:
            if (flow_path[1] == space) & (flow_path[2] > 0):  # flow rate which gets in
                ventilation_gain_coefficient = 1006. * 1.2 * flow_path[2] / 3600.
                if 'BC' in flow_path[0]:  # flow comes from outside
                    ventilation_losses[i] = (outdoor_temperature - air_temperature_temperatures_dict[space]) * ventilation_gain_coefficient * (1. - efficiency_heat_recovery)
                else:
                    ventilation_losses[i] = (air_temperature_temperatures_dict[flow_path[0]] - air_temperature_temperatures_dict[space]) * ventilation_gain_coefficient
    return ventilation_losses


def search_heatflux_spaces(hvac_flux, op_mode, setpoint, Ad, Bd, states_last, U, index_states, index_inputs, rad_share_hvac, radiative_share_sensor, ventilation_specific_flow_array, convective_internal_gains, radiative_internal_gains, internal_temperatures_dict, flow_array):

    # calculate ventilation losses
    outdoor_temperature = U[1]
    if op_mode == 'freefloat':
        space_air_temperature = get_states_from_index(states_last, index_states, 'spaces_air')
    else:
        space_air_temperature = setpoint

    # ventilation_gains = (outdoor_temperature - space_air_temperature) * ventilation_specific_flow_array
    ventilation_gains = calculate_ventilation_losses(flow_array, internal_temperatures_dict, outdoor_temperature)

    # apply current heat flux sent from solver
    convective_gains = hvac_flux * (1 - rad_share_hvac) + ventilation_gains + convective_internal_gains
    set_U_from_index(U, index_inputs, 'space_convective_gain', convective_gains)
    radiative_gains = hvac_flux * rad_share_hvac + radiative_internal_gains
    set_U_from_index(U, index_inputs, 'space_radiative_gain', radiative_gains)

    # calculate building states
    states = runStateSpace(Ad, Bd, states_last, U)
    # calculate difference on operative temperature
    air_temperature = get_states_from_index(states, index_states, 'spaces_air')
    mr_temperature = get_states_from_index(states, index_states, 'spaces_mean_radiant')
    estimated_temperatures = air_temperature * (1 - radiative_share_sensor) + mr_temperature * radiative_share_sensor
    # calculate error
    diff = setpoint - estimated_temperatures
    return diff


def operation_mode(indoor_temperature, outdoor_temperature, setpoint_heating, setpoint_cooling, n_spaces, op_modes):
    op_mode = [None] * n_spaces
    setpoint = np.zeros(n_spaces)
    threshold = (setpoint_heating + setpoint_cooling) / 2.
    for i in range(n_spaces):
        ref_temperature = indoor_temperature[i]
        if (ref_temperature <= threshold) and (outdoor_temperature < 15.):
            if 'heating' in op_modes:
                op_mode[i] = 'heating'
                setpoint[i] = setpoint_heating
            else:
                op_mode[i] = 'free_float'
                setpoint[i] = np.nan
        elif (ref_temperature > threshold) and (outdoor_temperature > 16.):
            if 'cooling' in op_modes:
                op_mode[i] = 'cooling'
                setpoint[i] = setpoint_cooling
            else:
                op_mode[i] = 'free_float'
                setpoint[i] = np.nan
        else:
            op_mode[i] = 'free_float'
            setpoint[i] = np.nan

    return op_mode, setpoint

# def space_temperature_control(mode, setpoint, Ad, Bd, states_0, U, hvac_flux_0, index_states, index_inputs, radiative_share_hvac, radiative_share_sensor, max_heating_power, max_cooling_power, ventilation_specific_flow_array, convective_internal_gains, radiative_internal_gains, internal_temperatures_dict, flow_array):
#     # does not work anymore with the new function for hybrid mode in building
#     # calculate hvac heat flux
#     if mode == 'heating':
#         hvac_flux = optimize.fsolve(search_heatflux_spaces, hvac_flux_0, args=(mode, setpoint, Ad, Bd, states_0, U, index_states, index_inputs, radiative_share_hvac, radiative_share_sensor, ventilation_specific_flow_array, convective_internal_gains, radiative_internal_gains, internal_temperatures_dict, flow_array), xtol=1.e-3)
#         heat_flux = np.clip(hvac_flux, 0., max_heating_power)
#     elif mode == 'cooling':
#         hvac_flux = optimize.fsolve(search_heatflux_spaces, hvac_flux_0, args=(mode, setpoint, Ad, Bd, states_0, U, index_states, index_inputs, radiative_share_hvac, radiative_share_sensor, ventilation_specific_flow_array, convective_internal_gains, radiative_internal_gains, internal_temperatures_dict, flow_array), xtol=1.e-3)
#         heat_flux = np.clip(hvac_flux, -max_cooling_power, 0.)
#     else:
#         heat_flux = hvac_flux_0 * 0.
#     return heat_flux

def space_temperature_control_simple(op_mode, setpoint, Ad, Bd, states_last, U, hvac_flux_last, index_states, index_inputs, radiative_share_hvac, radiative_share_sensor, max_heating_power, max_cooling_power, ventilation_specific_flow_array, ventilation_gain_coefficient, efficiency_heat_recovery, convective_internal_gains, radiative_internal_gains, internal_temperatures_dict, flow_array):

    outdoor_temperature = U[1]
    space_air_temperature = get_states_from_index(states_last, index_states, 'spaces_air')
    if flow_array == 0 or len(flow_array) == 0:
        ventilation_gains = (outdoor_temperature - space_air_temperature) * ventilation_gain_coefficient
    else:
        ventilation_gains = calculate_ventilation_losses(flow_array, internal_temperatures_dict, outdoor_temperature, efficiency_heat_recovery, ventilation_specific_flow_array)

    n_spaces = len(space_air_temperature)
    estimated_zone_temperature = np.zeros((n_spaces, 2))
    thermal_output_estimated = np.zeros(n_spaces)
    phi_inj = np.zeros((n_spaces, 2))

    for i in range(n_spaces):  # set minimum and maximum heating or cooling power
        if op_mode[i] == 'heating':
            phi_inj[i, :] = [0., max_heating_power]
        elif op_mode[i] == 'cooling':
            phi_inj[i, :] = [-max_cooling_power, 0.]
        else:
            phi_inj[i, :] = [0., 0.]

    if np.sum(np.abs(phi_inj)) > 1e-1:
        for n in range(2):  # minimum and maximum power
            # define convective and radiative heating/cooling share
            thermal_output_radiative_max = phi_inj[:, n] * radiative_share_hvac
            thermal_output_convective_max = phi_inj[:, n] * (1 - radiative_share_hvac)

            # apply current heat flux sent from solver
            convective_gains = thermal_output_convective_max + ventilation_gains + convective_internal_gains
            set_U_from_index(U, index_inputs, 'space_convective_gain', convective_gains)
            radiative_gains = thermal_output_radiative_max + radiative_internal_gains
            set_U_from_index(U, index_inputs, 'space_radiative_gain', radiative_gains)

            # get T0% and T100% for interpolation
            # calculate building states
            states = runStateSpace(Ad, Bd, states_last, U)
            estimated_zone_temperature[:, n] = get_states_from_index(states, index_states, 'spaces_air')

        # obtain ideal control values (temperature and power) from linear interpolation
        for i in range(n_spaces):
            delta_estimated = estimated_zone_temperature[i, 1] - estimated_zone_temperature[i, 0]
            delta_threshold = 0.001
            if np.sum(abs(delta_estimated)) < delta_threshold:
                thermal_output_estimated[i] = (phi_inj[i, 1] + phi_inj[i, 0]) / 2.
            elif op_mode[i] == 'heating':
                thermal_output_estimated[i] = min(max((setpoint[i] - estimated_zone_temperature[i, 0]) / delta_estimated * (phi_inj[i, 1] - phi_inj[i, 0]), phi_inj[i, 0]), phi_inj[i, 1])
            elif op_mode[i] == 'cooling':
                thermal_output_estimated[i] = max(min((estimated_zone_temperature[i, 1] - setpoint[i]) / delta_estimated * (phi_inj[i, 0] - phi_inj[i, 1]), phi_inj[i, 1]), phi_inj[i, 0])
            else:
                thermal_output_estimated[i] = 0.

    return thermal_output_estimated
