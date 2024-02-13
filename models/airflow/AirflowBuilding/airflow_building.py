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

class AirflowBuilding(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.air_temperature_dictionary = Variable("air_temperature_dictionary", 0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS, description="air_temperature_dictionary")
        self.pressures = Variable("pressures", value = 0, role=Roles.OUTPUTS, unit=Units.PASCAL, description="pressures")
        self.flow_rates = Variable("flow_rates", value = 0, role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_SECOND, description="flow_rates")

        self.my_weather = None

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
        #   Simulation parameters
        #################################################################################
        n_steps = len(my_weather.sky_temperature)
        dt = 3600

        #################################################################################
        #   Create pressure building model
        #################################################################################
        # pressure model
        boundary_matrix(my_weather, nodes, n_steps, dynamic_test=1,
                        apply_disturbance=[24, 0])  # sets external pressures
        my_P = P_Model('my_pressure_model')
        if self.case == 0:  # Colibri house
            my_P.pressure_model = True
        else:  # bestest, no pressure calculation
            my_P.pressure_model = False

        if my_P.pressure_model:
            try:
                my_P.matrix_model_init(n_steps, flow_paths, nodes, my_T.Space_list)
            except:
                raise ValueError(
                    'Pressure configuration does not correspond to thermal spaces. Change to pressure_model == False or correct')
            my_P.converged = False
            my_P.solver = 1  # 0=pingpong, 1=fully iterative

        else:  # simulate without pressure model
            my_P.flow_paths = my_P.nodes = my_P.flow_array = []
            my_P.pressures = 0
            my_P.pressures_last = 0
            my_P.converged = True

        my_P.found = []  # for convergence plot of pressure model
        self.my_P = my_P


    def run(self, time_step: int = 0, n_iteration: int = 0):

        niter_max = 0  # maximum number of internal (th-p) iterations

        if n_iteration == 1:

            # reset parameters for next time step
            self.my_P.niter = 0
            converged = False  # set to True at each time step, before iterating
            self.my_P.found = []

        # Pressure model
        if self.my_P.pressure_model:
            self.my_P.temperatures_update(self.air_temperature_dictionary)
            if self.my_P.solver == 1:  # iterative together with thermal model
                self.my_P.matrix_model_calc(time_step, n_iteration)
                self.my_P.matrix_model_check_convergence(n_iteration, niter_max)
            else:  # ping pong
                while (not self.my_P.converged or self.my_P.niter >= niter_max) & (n_iteration == 0):
                    self.my_P.matrix_model_calc(time_step, n_iteration)
                    self.my_P.matrix_model_check_convergence(n_iteration, niter_max)
                    self.my_P.niter += 1

            self.flow_rates = self.my_P.matrix_model_send_to_thermal(
                self.my_T.Space_list)  # send flow rate values to thermal model

        self.my_P.found.append(np.sum(self.my_P.pressures))  # for convergence plotting

        # save flux for next time step as initial guess
        self.my_P.pressures_last = self.my_P.pressures  # for next time step, start with last value

    def iteration_done(self, time_step: int = 0):
        self.my_P.matrix_model_set_results(time_step)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass

