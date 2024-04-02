
import numpy as np

from colibri.models.airflow.AirflowBuilding.boundary_conditions import boundary_matrix
from colibri.core.constants import *
from colibri.models.airflow.AirflowBuilding import connection_functions
from colibri.models.airflow.AirflowBuilding.utilities_peter_matrix import construct_nodes_sep, check_compatibility, \
    construct_CCi, gen_pressure_system, generate_AA_BB_pressure_system
from colibri.tests.data.data_model_coupling_Temp_Press import nodes, flow_paths

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.outputs import Outputs
from colibri.core.templates.parameters import Parameters
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import Roles, Units

class Airflow_Building(Model):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None

        self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.air_temperature_dictionary_input = Variable("air_temperature_dictionary", np.array(()), role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS, description="air_temperature_dictionary")
        self.pressures_output = Variable("pressures", value = np.array(()), role=Roles.OUTPUTS, unit=Units.PASCAL, description="pressures")
        self.flow_rates_output = Variable("flow_rates", value = np.array(()), role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_SECOND, description="flow_rates")

        self.my_weather = None

    def initialize(self) -> None:

        self.Space_list = self.project.building_data.space_list

        #################################################################################
        #   initialise weather data
        #################################################################################
        my_weather = self.project.get_weather()
        self.my_weather = my_weather

        #################################################################################
        #   Simulation parameters
        #################################################################################

        self.n_steps = len(my_weather.sky_temperature)

        #################################################################################
        #   Create pressure building model
        #################################################################################
        # pressure model
        boundary_matrix(my_weather, nodes, self.n_steps, dynamic_test=1,
                        apply_disturbance=[24, 0])  # sets external pressures

        if self.pressure_model:
            try:
                self.matrix_model_init(self.n_steps, flow_paths, nodes, self.Space_list)
            except Exception:
                raise ValueError(
                    'Pressure configuration does not correspond to thermal spaces. Change to pressure_model == False or correct')
            self.has_converged = False
            self.solver = 1  # 0=pingpong, 1=fully iterative

        else:  # simulate without pressure model
            self.flow_paths = self.nodes = self.flow_array = []
            self.pressures = 0
            self.pressures_last = 0
            self.has_converged = True

        self.found = []  # for convergence plot of pressure model

        self.air_temperature_dictionary = []

    def run(self, time_step: int = 0, n_iteration: int = 0):

        if not self.pressure_model:
            return

        niter_max = 0  # maximum number of internal (th-p) iterations

        if n_iteration == 1:

            # reset parameters for next time step
            self.niter = 0
            self.has_converged = False  # set to True at each time step, before iterating
            self.found = []

        # Pressure model
        if self.pressure_model:
            self.temperatures_update(self.air_temperature_dictionary_input)
            if self.solver == 1:  # iterative together with thermal model
                self.matrix_model_calc(time_step, n_iteration)
                self.matrix_model_check_convergence(n_iteration, niter_max)
            else:  # ping pong
                while (not self.has_converged or self.niter >= niter_max) & (n_iteration == 0):
                    self.matrix_model_calc(time_step, n_iteration)
                    self.matrix_model_check_convergence(n_iteration, niter_max)
                    self.niter += 1

            self.flow_rates = self.matrix_model_send_to_thermal(
                self.Space_list)  # send flow rate values to thermal model

        self.found.append(np.sum(self.pressures))  # for convergence plotting

        # save flux for next time step as initial guess
        self.pressures_last = self.pressures  # for next time step, start with last value

        # return outputs
        self.pressures_output = self.pressures
        self.flow_rates_output = self.flow_rates

    def converged(self, time_step: int = 0, n_iteration: int = 0) -> bool:
        return self.has_converged

    def iteration_done(self, time_step: int = 0):
        self.matrix_model_set_results(time_step)

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass


    def matrix_model_init(self, t_final, flow_paths, nodes, Space_list):

        # check if Spaces from thermal model correspond to nodes
        labels = []
        for space in Space_list:
            labels.append(space.label)
        for node in nodes:
            if nodes[node]['type'] == 'node':
                if node not in labels:
                    raise ValueError('Nodes in pressure model definitions do not correspond to spaces defined in th ethermal model')

        # define boundary and system pressure nodes
        self.boundary_nodes_ids, self.boundary_nodes_names, self.boundary_nodes_pressure, self.system_nodes_names, self.system_nodes_ids = construct_nodes_sep(nodes)

        # matrix with coefficients (kb values)
        self.CCa, self.CCb, self.n_CCa, self.n_CCb, self.BB_flow, self.U_flow_indexer, self.U_fan_indexer = construct_CCi(flow_paths, self.boundary_nodes_names, self.system_nodes_names)

        # check if all is connected as it should
        self.fan_suction_nodes = check_compatibility(self.boundary_nodes_names, flow_paths)

        # connectivity table
        self.CTa = np.argwhere(np.abs(self.CCa) > 1e-30)  # connectivity table to act like in sparse ...
        self.CTb = np.argwhere(np.abs(self.CCb) > 1e-30)  # connectivity table to act like in sparse ...

        # initialise flow matrix
        self.n_syst_nodes = len(self.system_nodes_ids)
        self.n_bound_nodes = len(self.boundary_nodes_ids)
        self.nominal_flowrate = 10./3600. * rho_ref  # any value, juste for initialising
        # initialise 2 flow matrices:
        self.FFa = np.ones((self.n_syst_nodes, self.n_syst_nodes)) * self.nominal_flowrate  # initial flow rate is nominal one in all segments
        self.FFb = np.ones((self.n_syst_nodes, self.n_bound_nodes)) * self.nominal_flowrate  # initial flow rate is nominal one in all segments
        # initialise 2 current flow matrices (for relaxation):
        self.FFa_act = np.ones((self.n_syst_nodes, self.n_syst_nodes)) * self.nominal_flowrate  # initial flow rate is nominal one in all segments
        self.FFb_act = np.ones((self.n_syst_nodes, self.n_bound_nodes)) * self.nominal_flowrate  # initial flow rate is nominal one in all segments

        # initial states of Network
        self.pressures = np.zeros((self.n_syst_nodes,1))             # initial node pressures to 0
        self.pressures_last = np.zeros((self.n_syst_nodes,1)) + 20.  # set a different pressure for previous time step

        # initialise results
        self.pressure_results = np.zeros((t_final, self.n_syst_nodes))
        # nodes[node]['pressure_list'] = np.zeros(t_final)

        # boudary connection arrays
        self.U_pressure = np.zeros((int(self.n_bound_nodes), 1))  # n pressure nodes in boundary
        self.U_flow = np.zeros((self.n_bound_nodes, 1))  # n injection nodes for flow rate by fans
        self.t_final = t_final
        self.nodes = nodes
        self.flow_paths = flow_paths

    def matrix_model_calc(self, t, niter):

            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # Set boundary condition for current time step
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            # U array for boundary conditions - pressure boundary nodes
            i = 0
            for node in self.nodes:
                if self.nodes[node]['type'] == 'boundary_condition':
                    dp_corr = 0.  # eventual correction (fan etc.)
                    self.nodes[node]['pressure'] = self.nodes[node]['pressure_list'][t]
                    self.nodes[node]['temperature'] = self.nodes[node]['temperature_list'][t]
                    rhobound = p_ref / (Rs_air * (t_ref_K + self.nodes[node]['temperature']))
                    rhoext = p_ref / (Rs_air * (t_ref_K + t_ext))
                    # pressure correction
                    dp_corr -= (rhoext - rhobound) * g * self.nodes[node]['z']
                    if node in self.fan_suction_nodes:
                        for f in range(len(self.U_fan_indexer)):
                            if node == self.U_fan_indexer[f][2]:  # this is the right one
                                id_to = self.U_fan_indexer[f][3]
                                id_from = self.U_fan_indexer[f][1]
                                connection = self.flow_paths[self.U_fan_indexer[f][0]]['connection']
                                flowrate = self.FFb_act[id_to, id_from]
                                sign = self.U_fan_indexer[f][4]
                                dp_corr += sign * connection_functions.fan_mechanical_calculate_dploss(flowrate=flowrate * 3600 / rho_ref,
                                                                                                       dplaw=connection['pressure_curve'])
                    self.nodes[node]['pressure'] += dp_corr
                    self.U_pressure[i, 0] = self.nodes[node]['pressure']  # set boundary pressures in U_pressure array
                    i += 1

            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # U fan array for boundary conditions - fan flow rates (imposed flow rates in pressure model)
            for flow_i in self.U_flow_indexer:
                connection = self.flow_paths[flow_i[0]]['connection']
                flowrate = connection['flow_rate']/3600.
                self.U_flow[flow_i[1], 0] = flowrate  # TODO: Check for sign !!!


            # CC update using flow rate. Use average flow with relaxation factor
            if niter > 0:
                smoothie = 0.5
                self.FFa_act = self.FFa * smoothie + self.FFa_act * (1-smoothie)
                self.FFb_act = self.FFb * smoothie + self.FFb_act * (1-smoothie)


            # generate the CCa_act and CCb_act matrices. with : C_act = C * flow_last_it ** (1/n-1)
            self.CCa_act, self.CCb_act = gen_pressure_system(self.CTa, self.CTb, self.FFa_act, self.FFb_act, self.CCa, self.CCb, self.n_CCa, self.n_CCb)

            # set AA and BB matrices and generate pressure matrix P and new flowrate matrix FF
            self.FFa, self.FFb, self.pressures = generate_AA_BB_pressure_system(self.U_pressure, self.U_flow, self.CCa_act, self.CCb_act, self.BB_flow, self.flow_paths, self.nodes, self.system_nodes_names)

    def matrix_model_check_convergence(self, niter, niter_max):

        # # check for difference from last time step
        delta_p = np.abs(self.pressures - self.pressures_last) / p_ref  # relative change from last iteration compared to reference pressure p_ref
        delta_p_max = np.abs(np.max(delta_p))  # take the maximum difference from all pressure nodes

        # check for convergence
        if (delta_p_max <= 1e-7) or (niter > niter_max):  # convergence if delta < threshold or at n_iter_max
            self.has_converged = True

        else:
            self.has_converged = False

        self.pressures_last = self.pressures  # keep pressure vector for next iteration step

    def matrix_model_set_results(self, t):
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Results
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # save data as in test Francois
        if self.pressure_model:
            self.pressure_results[t, :] = self.pressures[:,0]
            # write pressures in nodes dict
            i = 0
            for node in self.nodes:
                if self.nodes[node]['type'] != 'boundary_condition':
                    if t == 0:
                        self.nodes[node]['pressure_list'] = np.zeros(self.t_final)

                    self.nodes[node]['pressure_list'][t] = self.pressures[i,0]
                    i += 1

            # write results of flow rates in flow_paths dict
            for flow_path in self.flow_paths:
                if 'fanny' not in self.flow_paths[flow_path]['connection']['connection_type']:
                    if t == 0:
                        self.flow_paths[flow_path]['flow_rate_matrixcalc'] = np.zeros(self.t_final)
                    sign = self.flow_paths[flow_path]['flow_sign']
                    index_from = self.flow_paths[flow_path]['path_ids'][0]
                    index_to = self.flow_paths[flow_path]['path_ids'][1]
                    if self.flow_paths[flow_path]['flow_matrix'] == 'FFb':
                        self.flow_paths[flow_path]['flow_rate_matrixcalc'][t] = sign * self.FFb[index_from, index_to] * 3600
                    else:
                        self.flow_paths[flow_path]['flow_rate_matrixcalc'][t] = sign * self.FFa[index_from, index_to] * 3600

    def matrix_model_send_to_thermal(self, Space_list):
        flow_array = []
        for flow_path in self.flow_paths:
            path = self.flow_paths[flow_path]['path']
            sign = self.flow_paths[flow_path]['flow_sign']
            index_from = self.flow_paths[flow_path]['path_ids'][0]
            index_to = self.flow_paths[flow_path]['path_ids'][1]
            if self.flow_paths[flow_path]['flow_matrix'] == 'FFb':
                flowrate = sign * self.FFb[index_from, index_to] * 3600
            else:
                flowrate = sign * self.FFa[index_from, index_to] * 3600

            for space in Space_list:
                if path[0] == space.label:
                    if flowrate < 0:
                        flow_array.append([path[1], path[0], -flowrate])  # from other space into current space

                elif path[1] == space.label:
                    if flowrate > 0:
                        flow_array.append([path[0], path[1], flowrate])
        return flow_array


    def matrix_model_send_to_thermal_old(self, Space_list):
        flow_array = []
        for space in Space_list:
            for flow_path in self.flow_paths:
                path = self.flow_paths[flow_path]['path']
                sign = self.flow_paths[flow_path]['flow_sign']
                index_from = self.flow_paths[flow_path]['path_ids'][0]
                index_to = self.flow_paths[flow_path]['path_ids'][1]
                if (sign > 0) & (path[0] == space.label):
                    if self.flow_paths[flow_path]['flow_matrix'] == 'FFb':
                        flowrate = sign * self.FFb[index_from, index_to] * 3600
                    else:
                        flowrate = sign * self.FFa[index_from, index_to] * 3600
                    flow_array.append([path[0], path[1], flowrate])

                elif (sign < 0) & (path[1] == space.label):
                    if self.flow_paths[flow_path]['flow_matrix'] == 'FFb':
                        flowrate = sign * self.FFb[index_from, index_to] * 3600
                    else:
                        flowrate = sign * self.FFa[index_from, index_to] * 3600
                    flow_array.append([path[0], path[1], flowrate])
        return flow_array


    def temperatures_update(self, internal_temperatures_dict):
        # internal temperatures
        for temperature in internal_temperatures_dict:
            for node in self.nodes:
                if node == temperature:
                    self.nodes[node]['temperature'] = internal_temperatures_dict[temperature]
