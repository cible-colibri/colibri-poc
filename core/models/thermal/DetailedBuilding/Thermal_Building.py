import numpy as np

from core.constants import rho_ref, cp_air_ref
from core.Building import Building
from core.templates.inputs import Inputs
from core.model import Model
from core.templates.outputs import Outputs
from core.templates.parameters import Parameters
from core.variables.variable import Variable
from core.models.emitters.hydro_emitter import HydroEmitter
from core.models.thermal.DetailedBuilding.RyCj import generate_A_and_B, generate_euler_exp_Ad_Bd, runStateSpace, get_rad_shares,\
    set_U_from_index, get_states_from_index, get_u_values
from core.models.thermal.DetailedBuilding.controls import operation_mode, space_temperature_control_simple, calculate_ventilation_losses
from core.models.thermal.DetailedBuilding.generic import store_results
from core.models.utility.weather import solar_processor
from core.models.thermal.DetailedBuilding.results_handling import initialise_results
from utils.enums_utils import Roles, Units


class Thermal_Building(Building):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        super(Thermal_Building, self).__init__(name, inputs, outputs, parameters)

        self.name                  = name
        self.project               = None

        # parameters
        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.radiative_share_sensor = Variable("radiative_share_sensor", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="Radiative share between Tair and Tmr for operative temperature control. 1 = Tmr, 0=Tair")
        self.dt = Variable("dt", 3600, role=Roles.PARAMETERS, unit=Units.SECOND, description="Time step for the simulation ") #TODO: associate to the project instead of ThModel ?
        self.f_sky = Variable("f_sky", 0.5, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="Coefficient to connect the mean radiant temperature around the building f_sky = 0 --> Tmr = Tair, 1 --> Tmr=Fsky")
        self.radiative_share_internal_gains = Variable("radiative_share_internal_gains", 0.6, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="Radiative share for internal gains")
        self.iter_max = Variable("iter_max", 3, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="Number maximal of iteration")

        # inputs
        self.blind_position = Variable("blind_position", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="blind position, 1 = open")
        self.phi_radiative = Variable("phi_radiative", np.array(()), role=Roles.INPUTS, unit=Units.WATT, description="phi_radiative from emitter")
        self.phi_convective = Variable("phi_convective", np.array(()), role=Roles.INPUTS, unit=Units.WATT, description="phi_convective from emitter")
        self.phi_latent = Variable("phi_latent", np.array(()), role=Roles.INPUTS, unit=Units.WATT, description="phi_latent from emitter")

        # outputs
        self.air_temperature_dictionary_output = Variable("air_temperature_dictionary", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="air_temperature_dictionary")
        self.flow_rates_input = Variable("flow_rates", value = 0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_SECOND, description="flow_rates")

        # results to save
        self.heat_flux_vec = Variable("hvac_flux_vec", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT, description="hvac_flux_vec")

    def initialize(self) -> None:

        #################################################################################
        #   get weather data
        #################################################################################

        my_weather = self.project.get_weather()
        self.my_weather = my_weather

        #################################################################################
        #   Simulation parameters
        #################################################################################

        #TODO: passer en paramètre au niveau projet ?
        self.n_steps = len(my_weather.sky_temperature)

        #################################################################################
        #   Create thermal building model
        #################################################################################

        self.init_thermal_model(my_weather.weather_data, my_weather.latitude, my_weather.longitude, my_weather.time_zone)
        self.init_systems_parameters()

        #################################################################################
        #   Get control parameters
        #################################################################################

        self.setpoint_heating_vec = np.zeros(self.n_spaces)
        self.setpoint_cooling_vec = np.zeros(self.n_spaces)
        op_modes = []
        for i, space in enumerate(self.project.building_data.space_list):
            self.setpoint_heating_vec[i] = getattr(space, 'set_point_heating')
            self.setpoint_cooling_vec[i] = getattr(space, 'set_point_cooling')
            op_modes += getattr(space, 'op_modes')

        self.op_modes = np.unique(op_modes)

        #################################################################################
        #   Initialize parameters
        #################################################################################

        self.found = []  # for convergence plot of thermal model
        self.air_temperature_dictionary = self.reformat_for_pressure()
        self.flow_rates = []
        self.not_converged = True
        self.found = []
        self.switch = 0

        #################################################################################
        #   Initialize outputs
        #################################################################################

        self.phi_radiative = np.zeros(self.n_spaces)
        self.phi_convective = np.zeros(self.n_spaces)
        self.phi_latent = np.zeros(self.n_spaces)
        self.heat_flux_vec = np.zeros(self.n_spaces)

    def run(self, time_step: int = 0, n_iteration: int = 0):

        # pass inputs to model
        self.flow_array = self.flow_rates_input.value

        #################################################################################
        # control modes
        #################################################################################

        if n_iteration == 1:
            # calculate operation mode based on the results of the last time step
            self.air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
            self.op_mode, self.setpoint = operation_mode(self.air_temperatures,
                                                         self.my_weather.rolling_external_temperature[time_step],
                                                         self.setpoint_heating_vec,
                                                         self.setpoint_cooling_vec, self.n_spaces,
                                                         self.op_modes)


            # blind control
            self.blind_position = self.blind_position.value  # open = 1 np.clip(results['spaces_air'][:, t-1] < 25., 0.15, 1.)

            # reset parameters for next time step
            self.has_converged = False  # set to True at each time step, before iterating
            self.found = []

            # impose supply temperature from generator based on op mode
            for i, space in enumerate(self.project.building_data.space_list):
                emit = self.project.get_model_by_name(space.label + "_emitter")  # TODO: get by class ? -> create Space class
                if len(emit) > 0:
                    #TODO: créer un paramètre hydraulique. Est-ce que c'est à faire ici ce truc ??
                    if emit is HydroEmitter:
                        if self.op_mode[i] == 'cooling':
                            emit[0].temperature_in = emit[0].nominal_cooling_supply_temperature.value
                        elif self.op_mode[i] == 'heating':
                            emit[0].temperature_in = emit[0].nominal_heating_supply_temperature.value
                        else:
                            emit[0].temperature_in = emit[0].temperature_out.value  #TODO: last, pas last ? Pas initialisé en tout cas

        self.air_temperature_dictionary = self.reformat_for_pressure()  # send temperature values to pressure model

        #################################################################################
        # thermal model one at each time step, not in iteration
        #################################################################################

        # Thermal model
        self.calc_thermal_building_model_iter(time_step, self.my_weather)
        self.calc_convergence(threshold=1e-3)

        self.found.append(np.sum(self.hvac_flux_vec))  # for convergence plotting

        # return outputs
        self.air_temperature_dictionary_output = self.air_temperature_dictionary
        self.heat_flux_vec = self.hvac_flux_vec

    def converged(self, time_step: int = 0, n_iteration: int = 0) -> bool:
        return self.has_converged

    def iteration_done(self, time_step: int = 0):
        #convergence_plot(self.my_T.found, time_step, 1, 'Thermal', True)
        self.states_last = self.states
        self.hvac_flux_vec_last = self.hvac_flux_vec  # for next time step, start with last value

        store_results(time_step, self, self.my_weather)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")

    def check_units(self) -> None:
        pass

    def init_thermal_model(self, weather_data, latitude, longitude, time_zone):

        #################################################################################
        #   initialise thermal model
        #################################################################################

        self.n_spaces = len(self.project.building_data.space_list)

        # function to define radiative shares of wall surfaces inside a thermal zone
        get_rad_shares(self.project.building_data.boundary_list, self.project.building_data.window_list, self.project.building_data.space_list)

        # calculate global u-values for final balances of outputs (not for calculation)
        get_u_values(self.project.building_data.space_list)

        # create A and B matrices
        A, B, self.index_states, self.index_inputs = generate_A_and_B(self.project.building_data.space_list, self.project.building_data.boundary_list, self.project.building_data.window_list)

        # convert matrices to euler exponential
        self.Ad, self.Bd = generate_euler_exp_Ad_Bd(A, B, self.dt, label='None')

        # initialise several things
        self.n_inputs    = np.shape(B)[1]
        self.n_states    = np.shape(B)[0]
        self.U           = np.zeros(self.n_inputs)
        self.states      = np.zeros(self.n_states) + 20.  # states in order: boundary nodes, window nodes, air nodes, mean radiant nodes
        self.states_last = np.zeros(self.n_states) + 20.  # states in order: boundary nodes, window nodes, air nodes, mean radiant nodes

        # generate global dict where results can be saved
        #TODO: mettre dans la définition de la classe ? Mais pb connaissance de la taille des vecteurs
        self.results, self.res_list = initialise_results(self.index_states, self.project.building_data.space_list, self.project.building_data.boundary_list, self.n_steps)

        # create solar radiation matrix for all boundaries
        self.solar_bound_arriving_flux_matrix, self.solar_transmitted_flux_matrix = solar_processor(weather_data, latitude, longitude, self.project.building_data.boundary_list, self.project.building_data.space_list, time_zone)

        # radiative parameters
        self.boundary_absorption_array = np.zeros(len(self.project.building_data.boundary_list))
        for i, bound in enumerate(self.project.building_data.boundary_list):
            if bound.side_1 == 'exterior':
                self.boundary_absorption_array[i] = 1 - bound.albedo[0]
            else:
                self.boundary_absorption_array[i] = 1 - bound.albedo[1]

        # internal gains
        self.internal_gains_vec = np.zeros(self.n_spaces)
        for i, space in enumerate(self.project.building_data.space_list):
            self.internal_gains_vec[i] = getattr(space, 'constant_internal_gains')

    def init_systems_parameters(self):

        #################################################################################
        #   initialise thermal model
        #################################################################################

        # Heating and cooling system parameters
        self.hvac_flux_vec_last = np.zeros(self.n_spaces)
        self.window_losses = np.zeros(self.n_spaces)
        self.wall_losses = np.zeros(self.n_spaces)
        self.convective_gains_vec = np.zeros(self.n_spaces)
        self.radiative_gains_vec = np.zeros(self.n_spaces)
        self.radiative_share_hvac_vec = np.zeros(self.n_spaces)
        self.convective_internal_gains_vec = np.zeros(self.n_spaces)
        self.radiative_internal_gains_vec = np.zeros(self.n_spaces)
        self.max_heating_power_vec = np.zeros(self.n_spaces)  # #TODO: update each time step for hydronic
        self.max_cooling_power_vec = np.zeros(self.n_spaces)  # #TODO: update each time step for hydronic

        for i, space in enumerate(self.project.building_data.space_list):
            emit = self.project.get_model_by_name(space.label + "_emitter")  #TODO: get by class ? -> create Space class
            if len(emit) > 0:
                self.radiative_share_hvac_vec[i] = emit[0].radiative_share.value  #TODO: quid si plusieurs émetteurs mais pas du même mode ? ou pas du même radiative share ? (ex: poële + plancher chauffant)
                self.max_heating_power_vec[i] = emit[0].nominal_heating_power.value
                self.max_cooling_power_vec[i] = emit[0].nominal_cooling_power.value

        # ventilation parameters
        self.air_change_rate = 0.0
        self.efficiency_heat_recovery = 0.0  # exhaust ventilation, no heat recovery
        self.ventilation_gain_multiplier = np.zeros(self.n_spaces)
        for i, space in enumerate(self.project.building_data.space_list):
            self.ventilation_gain_multiplier[i] = space.volume * rho_ref * cp_air_ref
            self.air_change_rate += space.air_change_rate

    def calc_thermal_building_model_iter(self, t, weather):

        # weather data
        exterior_temperature_act = weather.ext_temperature[t]
        sky_temperature_act = weather.sky_temperature[t]
        ext_temperature_radiant = exterior_temperature_act * (1 - self.f_sky) + sky_temperature_act * self.f_sky
        ground_temperature_const = weather.ground_temperature[t]

        # set heat fluxes from internal gains and solar transmission
        self.convective_internal_gains_vec = self.internal_gains_vec * (1. - self.radiative_share_internal_gains)
        self.radiative_internal_gains_vec = self.solar_transmitted_flux_matrix[:, t] * self.blind_position + self.internal_gains_vec * self.radiative_share_internal_gains

        #TODO: comment faire pour initialiser plus tôt toutes ces matrices ?
        self.U = np.zeros(self.n_inputs)
        set_U_from_index(self.U, self.index_inputs, 'ground_temperature', ground_temperature_const)
        set_U_from_index(self.U, self.index_inputs, 'exterior_air_temperature', exterior_temperature_act)
        set_U_from_index(self.U, self.index_inputs, 'exterior_radiant_temperature', ext_temperature_radiant)
        set_U_from_index(self.U, self.index_inputs, 'radiative_gain_boundary_external', self.solar_bound_arriving_flux_matrix[:, t] * self.boundary_absorption_array)

        # ventilation preprocessing
        self.air_change_rate = self.air_change_rate  # could be variable
        self.efficiency_heat_recovery = self.efficiency_heat_recovery  # could be variable
        ventilation_gain_coefficient = self.ventilation_gain_multiplier * self.air_change_rate * (1. - self.efficiency_heat_recovery) / 3600.

        air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
        # emitter preprocessing
        for i, space in enumerate(self.project.building_data.space_list):
            emit = self.project.get_model_by_name(space.label + "_emitter")  #TODO: get by class ? -> create Space class
            if len(emit) > 0:
                if emit is HydroEmitter:  #TODO: suppose ideal
                    thermal_output_max = emit[0].nominal_UA * (emit[0].temperature_in - air_temperatures[i])
                    self.max_heating_power_vec[i] = max(0., thermal_output_max)
                    self.max_cooling_power_vec[i] = abs(min(0., thermal_output_max))
                else:
                    self.max_heating_power_vec[i] = emit[0].nominal_heating_power.value
                    self.max_cooling_power_vec[i] = emit[0].nominal_cooling_power.value

        # space heating control
        self.hvac_flux_vec = space_temperature_control_simple(self.op_mode, self.setpoint, self.Ad, self.Bd, self.states,
                                                          self.U, self.hvac_flux_vec_last, self.index_states,
                                                          self.index_inputs, self.radiative_share_hvac_vec,
                                                          self.radiative_share_sensor, self.max_heating_power_vec,
                                                          self.max_cooling_power_vec, self.ventilation_gain_multiplier, ventilation_gain_coefficient,
                                                          self.efficiency_heat_recovery, self.convective_internal_gains_vec,
                                                          self.radiative_internal_gains_vec, self.air_temperature_dictionary,
                                                          self.flow_array)

        # now apply the hvac_flux_vec and simulate the building a last time to obtain all results

        # set heat_flux for emitter - TODO: one of the Gurus (Enora, Peter) please check if this is the right spot to do this

        # emitter_list = [self.project.get_model_by_name(s.label + "_emitter") for s in self.project.building_data.space_list]
        # for emitter, flux in zip([found_emitters[0] for found_emitters in emitter_list if found_emitters], self.hvac_flux_vec):
        #     emitter.heat_demand = flux

        # recalculate ventilation losses
        if self.flow_array == 0 or len(self.flow_array) == 0:  # without pressure calculation, only use air change rates for all rooms
            # update coefficient for flow x cp x dT
            air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
            self.ventilation_gains = (exterior_temperature_act - air_temperatures) * ventilation_gain_coefficient
        else:
            # with flow matrix and airflow calculation
            self.ventilation_gains = calculate_ventilation_losses(self.flow_array, self.air_temperature_dictionary, exterior_temperature_act, self.efficiency_heat_recovery, self.ventilation_gain_multiplier)

        # set heat flux from controller for "official building simulation"
        self.convective_gains_vec = self.hvac_flux_vec * (1 - self.radiative_share_hvac_vec) + self.ventilation_gains + self.convective_internal_gains_vec
        set_U_from_index(self.U, self.index_inputs, 'space_convective_gain', self.convective_gains_vec)
        self.radiative_gains_vec = self.hvac_flux_vec * self.radiative_share_hvac_vec + self.radiative_internal_gains_vec
        set_U_from_index(self.U, self.index_inputs, 'space_radiative_gain', self.radiative_gains_vec)

        # apply corrected flux to the model
        self.states = runStateSpace(self.Ad, self.Bd, self.states_last, self.U)

        # for outputs
        self.window_gains = self.solar_transmitted_flux_matrix[:, t]

        #TODO: idem voir si dans une classe Space on veut y associer des résultats ou pas, si oui à chaque pas de temps ? en assessment en reprenant l'ensemble des matrices calculees ?

        # for i, space in enumerate(self.project.building_data.space_list):
        #     self.window_losses[i] = space.u_window * space.window_area * (ext_temperature_operative - air_temperatures[i])
        #     self.wall_losses[i] = space.u_wall * space.wall_area * (ext_temperature_operative - air_temperatures[i])

    def reformat_for_pressure(self):
        air_temperatures = get_states_from_index(self.states, self.index_states, 'spaces_air')
        temperatures_dict = {}
        for i, space in enumerate(self.project.building_data.space_list):
            temperatures_dict[space.label] = air_temperatures[i]
        return temperatures_dict

    def calc_convergence(self, threshold=1e-3):
        self.has_converged = np.sum(np.abs(self.hvac_flux_vec - self.hvac_flux_vec_last)) <= threshold

    def create_systems(self):

        project = self.project

        if not project:
            raise Exception('Project not defined - add me to a project first, so I can create systems with links')

        # create emitters
        for i, emitter in enumerate(project.building_data.emitter_list):
            type_id = emitter.type_id
            emitter_type = self.project.building_data.project_dict['archetype_collection']['emitter_types'][type_id]
            emitter_cls = emitter_type['model']
            zone_name = emitter.zone_name
            zone_index = project.building_data.get_zone_index(zone_name)
            emitter_name = zone_name + '_emitter'
            emitter_instance = Model.model_factory(emitter_cls, emitter_name)
            emitter_instance.zone_name = zone_name
            for param in emitter._fields:
                if hasattr(emitter, param):
                    setattr(emitter_instance, param, getattr(emitter, param))

            project.add(emitter_instance)

            # emitter -> building
            project.link_to_vector(emitter_instance, 'phi_radiative', self, 'phi_radiative', i)
            project.link_to_vector(emitter_instance, 'phi_convective', self, 'phi_convective', i)
            project.link_to_vector(emitter_instance, 'phi_latent', self, 'phi_latent', i)

            # building -> emitter
            project.link_from_vector(self, 'heat_flux_vec', zone_index, emitter_instance, 'heat_demand')

    def create_envelop(self):
        # for this, matrix based model, no models for walls, layers etc. are created
        # it used the data model directly to compute the matrices
        pass
