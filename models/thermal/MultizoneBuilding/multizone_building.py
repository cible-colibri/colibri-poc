from datetime import time

import numpy
import numpy as np
import pandas
import matplotlib.pyplot as plt


# ========================================
# Internal imports
# ========================================

from core.inputs       import Inputs
from core.model        import Model
from core.parameters   import Parameters
from core.outputs      import Outputs
from core.variable     import Variable
from models.thermal.vnat.test_cases.data_model_coupling_Temp_Press import nodes, flow_paths
from utils.enums_utils import (
                                Roles,
                                Units,
                               )

import matplotlib.pyplot as plt
from models.thermal.vnat.thermal_model.building_import import import_project
from models.thermal.vnat.thermal_model.RyCj import get_states_from_index
from models.thermal.vnat.thermal_model.controls import operation_mode
from models.thermal.vnat.thermal_model.weather_model import Weather
from models.thermal.vnat.thermal_model.bestest_cases import bestest_configs
from models.thermal.vnat.thermal_model.thermal_matrix_model import Th_Model
from models.thermal.vnat.thermal_model.generic import convergence_plot, print_results, plot_results, store_results
from models.thermal.vnat.aero_peter.matrix_aero import P_Model
from models.thermal.vnat.test_cases.boundary_conditions import boundary_matrix

class MultizoneBuilding(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.blind_position = Variable("blind_position", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="blind position, 1 = open")
        self.air_temperature_dictionary = Variable("air_temperature_dictionary", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="air_temperature_dictionary")
        self.flow_rates = Variable("flow_rates", value = 0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_SECOND, description="flow_rates")


    def initialize(self) -> None:
        # bestest case
        if self.case == 0:  # custom test
            file_name = 'house_1.json'
            epw_file = 'Paris.epw'  # old weather file
            time_zone = 'Europe/Paris'
        else:
            epw_file = 'DRYCOLDTMY.epw'  # old weather file
            # epw_file = '725650TYCST.epw'  # new weather file after update of standard in 2020
            time_zone = 'America/Denver'
            if self.case >= 900:
                file_name = 'house_bestest_900.json'
            elif self.case < 900:
                file_name = 'house_bestest_600.json'

        #################################################################################
        #   initialise weather data
        #################################################################################
        my_weather = Weather('my_weather')
        my_weather.init_weather(epw_file, time_zone)
        self.my_weather = my_weather

        #################################################################################
        #   Import project data
        #################################################################################
        # import data from json building description file
        project_dict = import_project(file_name)
        # adapt to bestest cases if necessary
        if self.case > 0:  # Bestest
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
        my_T.init_thermal_model(project_dict, my_weather.weather_data, my_weather.latitude, my_weather.longitude,
                                my_weather.time_zone, int_gains_trigger, infiltration_trigger, n_steps, dt)

        self.my_T = my_T

        my_T.found = []  # for convergence plot of thermal model

        #################################################################################
        #   Create thermal building model
        #################################################################################
        my_T = Th_Model('myhouse')
        my_T.init_thermal_model(project_dict, my_weather.weather_data, my_weather.latitude, my_weather.longitude, my_weather.time_zone, int_gains_trigger, infiltration_trigger, n_steps, dt)

    def run(self, time_step: int = 0, n_iteration: int = 0):

        niter_max = 0  # maximum number of internal (th-p) iterations

        if n_iteration == 1:
            #################################################################################
            # thermal model one at each time step, not in iteration
            #################################################################################
            # calculate operation mode based on the results of the last time step
            self.my_T.air_temperatures = get_states_from_index(self.my_T.states, self.my_T.index_states, 'spaces_air')
            self.my_T.op_mode, self.my_T.setpoint = operation_mode(self.my_T.air_temperatures,
                                                                   self.my_weather.rolling_external_temperature[time_step],
                                                                   self.my_T.setpoint_heating,
                                                                   self.my_T.setpoint_cooling, self.my_T.n_spaces,
                                                                   self.my_T.free_float)

            # blind control
            self.my_T.blind_position = self.blind_position.value  # open = 1 np.clip(results['spaces_air'][:, t-1] < 25., 0.15, 1.)

            # reset parameters for next time step
            converged = False  # set to True at each time step, before iterating
            self.my_T.found = []

        self.air_temperature_dictionary = self.my_T.send_to_pressure()  # send temperature values to pressure model

        # Thermal model
        self.my_T.air_temperature_dictionary = self.air_temperature_dictionary # refactor
        self.my_T.flow_array = self.flow_rates
        self.my_T.calc_thermal_building_model_iter(time_step, self.my_weather)
        self.my_T.calc_convergence(threshold=1e-3)

        self.my_T.found.append(np.sum(self.my_T.hvac_flux))  # for convergence plotting

        # save flux for next time step as initial guess
        self.my_T.hvac_flux_0 = self.my_T.hvac_flux  # for next time step, start with last value

        self.air_temperatures = self.my_T.air_temperatures

    def iteration_done(self, time_step: int = 0):
        self.my_T.states_0 = self.my_T.states
        store_results(time_step, self.my_T, self.my_weather)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass

