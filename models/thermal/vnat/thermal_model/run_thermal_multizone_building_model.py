# -*- coding: utf-8 -*-
import time
import numpy as np
from data.Building.building_import import import_project
from models.thermal.vnat.thermal_model.RyCj import get_states_from_index
from models.thermal.vnat.thermal_model.controls import operation_mode
from models.utility.weather import Weather
from models.thermal.vnat.thermal_model.bestest_cases import bestest_configs
from models.thermal.vnat.thermal_model.thermal_matrix_model import Th_Model
from models.thermal.vnat.thermal_model.generic import convergence_plot, print_results, plot_results, store_results
from models.thermal.vnat.aero_peter.matrix_aero import P_Model
from models.thermal.vnat.test_cases.data_model_coupling_Temp_Press import nodes, flow_paths
from models.thermal.vnat.test_cases.boundary_conditions import boundary_matrix


def simulate_project(file_name='house_1_1.json'):

    # simulation start timer
    start = time.time()

    # bestest case
    case = 0
    if case == 0:  # custom test
        file_name = 'house_1.json'
        # file_name = 'house_100m2.json'
        epw_file = 'Paris.epw'  # old weather file
        time_zone = 'Europe/Paris'
    else:
        epw_file = 'DRYCOLDTMY.epw'  # old weather file
        # epw_file = '725650TYCST.epw'  # new weather file after update of standard in 2020
        time_zone = 'America/Denver'
        if case >= 900:
            file_name = 'house_bestest_900.json'
        elif case < 900:
            file_name = 'house_bestest_600.json'
        epw_file = 'Paris.epw'  # old weather file
        time_zone = 'Europe/Paris'

    #################################################################################
    #   initialise weather data
    #################################################################################
    my_weather = Weather('my_weather')
    my_weather.init_weather(epw_file, time_zone)

    #################################################################################
    #   Import project data
    #################################################################################
    # import data from json building description file
    project_dict = import_project(file_name)
    # adapt to bestest cases if necessary
    if case > 0:  # Bestest
        project_dict, int_gains_trigger, infiltration_trigger = bestest_configs(project_dict, case)
    else:
        int_gains_trigger = infiltration_trigger = 1.

    #################################################################################
    #   Simulation parameters
    #################################################################################
    n_steps = len(my_weather.sky_temperature)
    dt = 3600

    #################################################################################
    #   Create thermal building model
    #################################################################################
    my_T = Th_Model('myhouse')
    my_T.init_thermal_model(project_dict, my_weather.weather_data, my_weather.latitude, my_weather.longitude, my_weather.time_zone, int_gains_trigger, infiltration_trigger, n_steps, dt)

    #################################################################################
    #   Create pressure building model
    #################################################################################
    # pressure model
    boundary_matrix(my_weather, nodes, n_steps, dynamic_test=1, apply_disturbance=[24, 0])  # sets external pressures
    my_P = P_Model('my_pressure_model')
    if case == 0:  # Colibri house
        my_P.pressure_model = True
    else:  # bestest, no pressure calculation
        my_P.pressure_model = False

    if my_P.pressure_model:
        try:
            my_P.matrix_model_init(n_steps, flow_paths, nodes, my_T.Space_list)
        except Exception:
            raise ValueError('Pressure configuration does not correspond to thermal spaces. Change to pressure_model == False or correct')
        my_P.converged = False
        my_P.solver = 1  # 0=pingpong, 1=fully iterative

    else:  # simulate without pressure model
        my_P.flow_paths = my_P.nodes = my_P.flow_array = []
        my_P.pressures = 0
        my_P.pressures_last = 0
        my_P.converged = True

    #################################################################################
    #       simulation parameters
    #################################################################################
    niter_max = 100  # maximum number of iterations
    to_plot = True
    plot_convergence = False
    my_T.found = []  # for convergence plot of thermal model
    my_P.found = []  # for convergence plot of pressure model

    #################################################################################
    #       simulation loop
    #################################################################################

    for t in range(n_steps):  # time loop

        #################################################################################
        # thermal model one at each time step, not in iteration
        #################################################################################
        # calculate operation mode based on the results of the last time step
        my_T.air_temperatures = get_states_from_index(my_T.states, my_T.index_states, 'spaces_air')
        my_T.op_mode, my_T.setpoint = operation_mode(my_T.air_temperatures, my_weather.rolling_external_temperature[t], my_T.setpoint_heating, my_T.setpoint_cooling, my_T.n_spaces, my_T.op_modes)

        # blind control
        my_T.blind_position = 1.  # open = 1 np.clip(results['spaces_air'][:, t-1] < 25., 0.15, 1.)

        # reset parameters for next time step
        niter = 100  # set number of iteration to 0 at each time step
        my_P.niter = 0
        converged = False  # set to True at each time step, before iterating
        my_T.found = []
        my_P.found = []

        # my_T.hvac_flux_vec_0 = my_T.hvac_flux_vec_0*0.  # for next time step, start with last value
        # my_P.pressures_last = my_P.pressures_last*0.  # for next time step, start with last value

        while not converged:  # iterative loop

            # myPhanie.run()
            # my_T.run()
            # my_P.run()
            # if (my_T.converged & my_P.converged & my_Phanie.converged) or (niter >= niter_max):
            #     converged = True

            my_T.air_temperature_dictionary = my_T.reformat_for_pressure()  # send temperature values to pressure model

            # Pressure model
            if my_P.pressure_model:
                my_P.temperatures_update(my_T.air_temperature_dictionary)
                if my_P.solver == 1:  # iterative together with thermal model
                    my_P.matrix_model_calc(t, niter)
                    my_P.matrix_model_check_convergence(niter, niter_max)
                else:  # ping pong
                    while (not my_P.converged or my_P.niter >= niter_max) & (niter == 0):
                        my_P.matrix_model_calc(t, niter)
                        my_P.matrix_model_check_convergence(niter, niter_max)
                        my_P.niter += 1

                my_P.flow_array = my_P.matrix_model_send_to_thermal(my_T.Space_list)  # send flow rate values to thermal model

            # Thermal model
            my_T.flow_array = my_P.flow_array
            my_T.calc_thermal_building_model_iter(t, my_weather)
            my_T.calc_convergence(threshold=1e-3)

            my_T.found.append(np.sum(my_T.hvac_flux_vec))  # for convergence plotting
            my_P.found.append(np.sum(my_P.pressures))  # for convergence plotting

            if (my_T.converged & my_P.converged) or (niter >= niter_max):
                converged = True
                my_T.states_last = my_T.states
                convergence_plot(my_T.found, t, niter, 'Thermal', plot_convergence)
                convergence_plot(my_P.found, t, niter, 'Pressure', plot_convergence)
                store_results(t, my_T, my_weather)
                my_P.matrix_model_set_results(t)
            else:
                converged = False
                niter += 1

            # save flux for next time step as initial guess
            my_T.hvac_flux_vec_last = my_T.hvac_flux_vec  # for next time step, start with last value
            my_P.pressures_last = my_P.pressures  # for next time step, start with last value


    my_T.results['av_outdoor_heating_temperature'] = np.mean(my_T.results['outdoor_temperatures'][0][my_T.results['hvac_flux_vec'][0]>0.1])
    print('###################################################################')
    print('Simulation time: ', np.round(time.time() - start, 3), 's')
    print('###################################################################')

    print_results(my_T)
    print('average ambient heating season temperature : ', my_T.results['av_outdoor_heating_temperature'])
    plot_results(my_T.results, to_plot)

if __name__ == '__main__':
    simulate_project()
