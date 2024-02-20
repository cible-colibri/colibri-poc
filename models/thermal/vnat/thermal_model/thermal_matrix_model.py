import numpy as np
import time
import numpy as np
import matplotlib.pyplot as plt

from core.inputs import Inputs
from core.model import Model
from core.outputs import Outputs
from core.parameters import Parameters
from core.variable import Variable
from models.thermal.vnat.thermal_model.building_import import import_project, import_spaces, import_boundaries
from models.thermal.vnat.thermal_model.RyCj import generate_A_and_B, generate_euler_exp_Ad_Bd, runStateSpace, get_rad_shares,\
    set_U_from_index, get_states_from_index, get_u_values
from models.thermal.vnat.thermal_model.controls import operation_mode, space_temperature_control_simple, calculate_ventilation_losses
from models.thermal.vnat.thermal_model.generic import store_results
from models.thermal.vnat.thermal_model.weather_model import import_epw_weather, solar_processor, Weather
from models.thermal.vnat.test_cases.data_model import rho_ref, cp_air_ref
from models.thermal.vnat.thermal_model.bestest_cases import bestest_configs
from models.thermal.vnat.thermal_model.results_handling import initialise_results
from utils.enums_utils import Roles, Units


class Th_Model(Model):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.blind_position = Variable("blind_position", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="blind position, 1 = open")

        self.air_temperature_dictionary_output = Variable("air_temperature_dictionary", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="air_temperature_dictionary")
        self.flow_rates_input = Variable("flow_rates", value = 0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_SECOND, description="flow_rates")

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
        self.init_thermal_model(project_dict, my_weather.weather_data, my_weather.latitude, my_weather.longitude,
                                my_weather.time_zone, int_gains_trigger, infiltration_trigger, n_steps, dt)

        self.found = []  # for convergence plot of thermal model

        self.air_temperature_dictionary = self.send_to_pressure()
        self.flow_rates = []

    def run(self, time_step: int = 0, n_iteration: int = 0):

        # pass inputs to model
        self.flow_array = self.flow_rates_input.value

        niter_max = 0  # maximum number of internal (th-p) iterations

        if n_iteration == 1:
            #################################################################################
            # thermal model one at each time step, not in iteration
            #################################################################################
            # calculate operation mode based on the results of the last time step
            self.air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
            self.op_mode, self.setpoint = operation_mode(self.air_temperatures,
                                                                   self.my_weather.rolling_external_temperature[time_step],
                                                                   self.setpoint_heating,
                                                                   self.setpoint_cooling, self.n_spaces,
                                                                   self.op_modes)


            # blind control
            self.blind_position = self.blind_position.value  # open = 1 np.clip(results['spaces_air'][:, t-1] < 25., 0.15, 1.)

            # reset parameters for next time step
            self.has_converged = False  # set to True at each time step, before iterating
            self.found = []

        self.air_temperature_dictionary = self.send_to_pressure()  # send temperature values to pressure model

        # Thermal model
        self.calc_thermal_building_model_iter(time_step, self.my_weather)
        self.calc_convergence(threshold=1e-3)

        self.found.append(np.sum(self.hvac_flux))  # for convergence plotting

        # save flux for next time step as initial guess
        self.hvac_flux_last = self.hvac_flux  # for next time step, start with last value

        # return outputs
        self.air_temperature_dictionary_output = self.air_temperature_dictionary

    def converged(self):
        return self.has_converged

    def iteration_done(self, time_step: int = 0):
        #convergence_plot(self.my_T.found, time_step, 1, 'Thermal', True)
        self.states_0 = self.states
        store_results(time_step, self, self.my_weather)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass

    def init_thermal_model(self, project_dict, weather_data, latitude, longitude, time_zone, int_gains_trigger=1, infiltration_trigger=1, n_steps = 8760, dt=3600):

        #################################################################################
        #   initialise thermal model
        #################################################################################

        # load data into lists of dicts with boundaries, windows and spaces
        Boundary_list, Window_list = import_boundaries(project_dict)
        Space_list = import_spaces(project_dict)
        self.n_spaces = len(Space_list)

        # function to define radiative shares of wall surfaces inside a thermal zone
        get_rad_shares(Boundary_list, Window_list, Space_list)

        # calculate global u-values for final balances of outputs (not for calculation)
        get_u_values(Space_list)

        # create A and B matrices
        A, B, self.index_states, self.index_inputs = generate_A_and_B(Space_list, Boundary_list, Window_list)

        # convert matrices to euler exponential
        self.Ad, self.Bd = generate_euler_exp_Ad_Bd(A, B, dt, label='None')

        # initialise several things
        self.n_inputs = np.shape(B)[1]
        self.n_states = np.shape(B)[0]
        self.U = np.zeros(self.n_inputs)
        self.states = np.zeros(self.n_states) + 20.  # states in order: boundary nodes, window nodes, air nodes, mean radiant nodes
        self.states_last = np.zeros(self.n_states) + 20.  # states in order: boundary nodes, window nodes, air nodes, mean radiant nodes

        # generate global dict where results can be saved
        self.results, self.res_list = initialise_results(self.index_states, Space_list, Boundary_list, n_steps)

        # create solar radiation matrix for all boundaries
        self.solar_bound_arriving_flux_matrix, self.solar_transmitted_flux_matrix = solar_processor(weather_data, latitude, longitude, Boundary_list, Space_list, time_zone)
        # radiative parameters
        self.boundary_absorption_array = np.zeros(len(Boundary_list))
        for i, bound in enumerate(Boundary_list):
            if bound.side_1 == 'exterior':
                self.boundary_absorption_array[i] = 1 - bound.albedo[0]
            else:
                self.boundary_absorption_array[i] = 1 - bound.albedo[1]
        self.f_sky = 0.5  # coefficient to connect the mean radiant temperature around the building f_sky = 0 --> Tmr = Tair, 1 --> Tmr=Fsky

        # controls parameters
        self.radiative_share_sensor = 0.0  # this is where you control on
        self.setpoint_heating = 20.
        self.setpoint_cooling = 27.
        self.op_modes = ['heating', 'cooling']

        # HVAC system parameters
        self.radiative_share_hvac = 0.0  # radiative share of heat emission of emitter
        self.max_heating_power = 10000.
        self.max_cooling_power = 10000.
        self.hvac_flux_last = np.zeros(self.n_spaces)
        self.window_losses = np.zeros(self.n_spaces)
        self.wall_losses = np.zeros(self.n_spaces)

        # internal gains
        self.int_gains_trigger = int_gains_trigger
        self.internal_gains = int_gains_trigger * 200.
        self.radiative_share_internal_gains = 0.6
        self.space_floor_area_array = np.zeros(self.n_spaces)
        for i in range(self.n_spaces):
            self.space_floor_area_array[i] = 1. #Space_list[i].reference_area (if gains are given in W/m2
        self.internal_gains_array = self.internal_gains * self.space_floor_area_array

        # ventilation parameters
        self.infiltration_trigger = infiltration_trigger
        self.air_change_rate = infiltration_trigger * 0.41
        self.efficiency_heat_recovery = 0.0  # exhaust ventilation, no heat recovery
        self.ventilation_gain_multiplier = np.zeros(self.n_spaces)
        for i, space in enumerate(Space_list):
            self.ventilation_gain_multiplier[i] = space.volume * rho_ref * cp_air_ref

        self.not_converged = True
        self.iter_max = 3
        self.plot_convergence = True
        self.found = []
        self.switch = 0

        self.Boundary_list = Boundary_list
        self.Window_list = Window_list
        self.Space_list = Space_list


    def calc_thermal_building_model_iter(self, t, weather):

        # weather data
        exterior_temperature_act = weather.ext_temperature[t]
        # rolling_exterior_temperature_act = weather.rolling_external_temperature[t]
        sky_temperature_act = weather.sky_temperature[t]
        ground_temperature_const = 10.

        # set heat fluxes from internal gains and solar transmission
        self.convective_internal_gains = self.internal_gains_array * (1. - self.radiative_share_internal_gains)
        self.radiative_internal_gains = self.solar_transmitted_flux_matrix[:, t] * self.blind_position + self.internal_gains_array * self.radiative_share_internal_gains
        ext_temperature_operative = exterior_temperature_act * (1 - self.f_sky) + sky_temperature_act * self.f_sky

        self.U = np.zeros(self.n_inputs)
        set_U_from_index(self.U, self.index_inputs, 'ground_temperature', ground_temperature_const)
        set_U_from_index(self.U, self.index_inputs, 'exterior_air_temperature', exterior_temperature_act)
        set_U_from_index(self.U, self.index_inputs, 'exterior_radiant_temperature', ext_temperature_operative)
        set_U_from_index(self.U, self.index_inputs, 'radiative_gain_boundary_external', self.solar_bound_arriving_flux_matrix[:, t] * self.boundary_absorption_array)

        # ventilation preprocessing
        self.air_change_rate = self.air_change_rate  # could be variable
        self.efficiency_heat_recovery = self.efficiency_heat_recovery  # could be variable
        ventilation_gain_coefficient = self.ventilation_gain_multiplier * self.air_change_rate * (1. - self.efficiency_heat_recovery) / 3600.

        # space heating control
        self.hvac_flux = space_temperature_control_simple(self.op_mode, self.setpoint, self.Ad, self.Bd, self.states,
                                                          self.U, self.hvac_flux_last, self.index_states,
                                                          self.index_inputs, self.radiative_share_hvac,
                                                          self.radiative_share_sensor, self.max_heating_power,
                                                          self.max_cooling_power, self.ventilation_gain_multiplier, ventilation_gain_coefficient,
                                                          self.efficiency_heat_recovery, self.convective_internal_gains,
                                                          self.radiative_internal_gains, self.air_temperature_dictionary,
                                                          self.flow_array)

        # now apply the hvac_flux and simulate the building a last time to obtain all results
        # recalculate ventilation losses
        if self.flow_array == 0 or len(self.flow_array) == 0:  # without pressure calculation, only use air change rates for all rooms
            # update coefficient for flow x cp x dT
            air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
            self.ventilation_gains = (exterior_temperature_act - air_temperatures) * ventilation_gain_coefficient
        else:
            # with flow matrix and airflow calculation
            self.ventilation_gains = calculate_ventilation_losses(self.flow_array, self.air_temperature_dictionary, exterior_temperature_act, self.efficiency_heat_recovery, self.ventilation_gain_multiplier)

        # set heat flux from controller for "official building simulation"
        self.convective_gains = self.hvac_flux * (1 - self.radiative_share_hvac) + self.ventilation_gains + self.convective_internal_gains
        set_U_from_index(self.U, self.index_inputs, 'space_convective_gain', self.convective_gains)
        self.radiative_gains = self.hvac_flux * self.radiative_share_hvac + self.radiative_internal_gains
        set_U_from_index(self.U, self.index_inputs, 'space_radiative_gain', self.radiative_gains)

        # apply corrected flux to the model
        self.states = runStateSpace(self.Ad, self.Bd, self.states_last, self.U)
        # for outputs
        self.window_gains = self.solar_transmitted_flux_matrix[:, t]
        # for i, space in enumerate(self.Space_list):
        #     self.window_losses[i] = space.u_window * space.window_area * (ext_temperature_operative - air_temperatures[i])
        #     self.wall_losses[i] = space.u_wall * space.wall_area * (ext_temperature_operative - air_temperatures[i])


    def send_to_pressure(self):
        air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
        temperatures_dict = {}
        for i, space in enumerate(self.Space_list):
            temperatures_dict[space.label] = air_temperatures[i]
        return temperatures_dict

    def calc_convergence(self, threshold=1e-3):
        self.has_converged = np.sum(np.abs(self.hvac_flux - self.hvac_flux_last)) <= threshold