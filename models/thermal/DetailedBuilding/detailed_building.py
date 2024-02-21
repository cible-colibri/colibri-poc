import numpy as np

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

from models.thermal.vnat.thermal_model.building_import import import_project
from models.thermal.vnat.thermal_model.RyCj import get_states_from_index
from models.thermal.vnat.thermal_model.controls import operation_mode
from models.utility.weather import Weather
from models.thermal.vnat.thermal_model.bestest_cases import bestest_configs
from models.thermal.vnat.thermal_model.thermal_matrix_model import Th_Model
from models.thermal.vnat.thermal_model.generic import store_results
from models.thermal.vnat.aero_peter.matrix_aero import P_Model
from models.thermal.vnat.test_cases.boundary_conditions import boundary_matrix

class DetailedBuilding(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.blind_position = Variable("blind_position", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="blind position, 1 = open")
        self.air_temperatures = Variable("air_temperatures", value = 20, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="The operative temperature for each airnode")


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

        self.my_P = my_P

        my_T.found = []  # for convergence plot of thermal model
        my_P.found = []  # for convergence plot of pressure model

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
        if self.case == 0:  # Colibri house
            my_P.pressure_model = True
        else:  # bestest, no pressure calculation
            my_P.pressure_model = False

        if my_P.pressure_model:
            try:
                my_P.matrix_model_init(n_steps, flow_paths, nodes, my_T.Space_list)
            except:
                raise ValueError('Pressure configuration does not correspond to thermal spaces. Change to pressure_model == False or correct')
            my_P.converged = False
            my_P.solver = 1  # 0=pingpong, 1=fully iterative

        else:  # simulate without pressure model
            my_P.flow_paths = my_P.nodes = my_P.flow_array = []
            my_P.pressures = 0
            my_P.pressures_last = 0
            my_P.converged = True

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
            self.my_P.niter = 0
            converged = False  # set to True at each time step, before iterating
            self.my_T.found = []
            self.my_P.found = []

        self.my_T.air_temperature_dictionary = self.my_T.send_to_pressure()  # send temperature values to pressure model

        # Pressure model
        if self.my_P.pressure_model:
            self.my_P.temperatures_update(self.my_T.air_temperature_dictionary)
            if self.my_P.solver == 1:  # iterative together with thermal model
                self.my_P.matrix_model_calc(time_step, n_iteration)
                self.my_P.matrix_model_check_convergence(n_iteration, niter_max)
            else:  # ping pong
                while (not self.my_P.converged or self.my_P.niter >= niter_max) & (n_iteration == 0):
                    self.my_P.matrix_model_calc(time_step, n_iteration)
                    self.my_P.matrix_model_check_convergence(n_iteration, niter_max)
                    self.my_P.niter += 1

            self.my_P.flow_array = self.my_P.matrix_model_send_to_thermal(
                self.my_T.Space_list)  # send flow rate values to thermal model

        # Thermal model
        self.my_T.flow_array = self.my_P.flow_array
        self.my_T.calc_thermal_building_model_iter(time_step, self.my_weather)
        self.my_T.calc_convergence(threshold=1e-3)

        self.my_T.found.append(np.sum(self.my_T.hvac_flux))  # for convergence plotting
        self.my_P.found.append(np.sum(self.my_P.pressures))  # for convergence plotting

        # save flux for next time step as initial guess
        self.my_T.hvac_flux_0 = self.my_T.hvac_flux  # for next time step, start with last value
        self.my_P.pressures_last = self.my_P.pressures  # for next time step, start with last value

        self.air_temperatures = self.my_T.air_temperatures

    def converged(self):
        return self.my_P.converged and self.my_T.converged

    def iteration_done(self, time_step: int = 0):
        self.my_T.states_0 = self.my_T.states
        store_results(time_step, self.my_T, self.my_weather)
        self.my_P.matrix_model_set_results(time_step)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass

