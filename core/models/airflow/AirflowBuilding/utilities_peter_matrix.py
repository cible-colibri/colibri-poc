import numpy as np
import copy
from scipy.linalg import inv
from core.constants import *
from core.models.airflow.AirflowBuilding import connection_functions


def construct_nodes_sep(nodes):

    """
    function that allows to separate boundary and internal system nodes
    :param nodes : nodes dictionary from data set

    :return: boundary_nodes_ids :  array with id's of boundary nodes
    :return: boundary_nodes_names :  array with names of boundary nodes
    :return: boundary_nodes_pressure :  array with pressures of boundary nodes
    :return: system_nodes_names :  array with names of system nodes
    :return: system_nodes_ids :  array with id's of system nodes

    """
    boundary_nodes_ids = []
    boundary_nodes_names = []
    boundary_nodes_pressure = []
    i_b = 0  # boundary counter
    system_nodes_ids = []
    system_nodes_names = []
    i_s = 0  # system node counter
    for i in nodes:
        if nodes[i]['type'] == 'boundary_condition':
            boundary_nodes_names.append(i)
            boundary_nodes_ids.append(i_b)
            boundary_nodes_pressure.append(nodes[i]['pressure'])
            i_b += 1
        if nodes[i]['type'] == 'node':
            system_nodes_names.append(i)
            system_nodes_ids.append(i_s)
            i_s += 1

    return boundary_nodes_ids, boundary_nodes_names, boundary_nodes_pressure, system_nodes_names, system_nodes_ids


def check_compatibility(boundary_nodes_names, flow_paths):

    """
    function that allows to separate boundary and internal system nodes
    :param nodes : nodes dictionary from data set
    :param flow_paths: flow_paths dictionary from data model
    :return:

    """
    fan_suction_nodes = []
    other_inlet_nodes = []

    for j, flow_path in enumerate(flow_paths):
        id_0_name = flow_paths[flow_path]['path'][0]
        id_1_name = flow_paths[flow_path]['path'][1]
        if 'fan' in flow_paths[flow_path]['connection']['connection_type']:
            if id_0_name in boundary_nodes_names:
                fan_suction_nodes.append(id_0_name)
            elif id_1_name in boundary_nodes_names:
                fan_suction_nodes.append(id_1_name)
            else:
                raise ValueError('The fan in flow path ' + flow_path + ' is not connected to an external boundary pressure. Please verify your configuration')
        else:  # other flow path than fan
            if id_0_name in boundary_nodes_names:
                other_inlet_nodes.append(id_0_name)
            elif id_1_name in boundary_nodes_names:
                other_inlet_nodes.append(id_1_name)

    # now check that the boundary pressure for each fan suction is unique
    set1 = set(fan_suction_nodes)
    set2 = set(other_inlet_nodes)
    common_elements = set1.intersection(set2)
    if len(common_elements) >= 1:
        raise ValueError('Fan boundary node is at the same time boundary node for another inlet, which is not allowed. Please specify another boudnary node')

    return fan_suction_nodes


def construct_CCi(flow_paths, boundary_nodes_names, system_nodes_names):

    """
    Generate CCa and CCb matrices with pressure drop coefficients (used later to construct A matrix of pressure system)
    :param flow_paths: flow_paths dictionary from data model
    :param boundary_nodes_names: array of boundary names
    :param system_nodes_names: array of system node names

    :return: CCa: flow resistance coefficient matrix between system nodes
    :return: CCb: flow resistance coefficient matrix between boundary and system nodes

    """
    n_syst_nodes = len(system_nodes_names)
    n_bound_nodes = len(boundary_nodes_names)

    # Matrices for air exchange due to pressure differences
    CCa = np.zeros((n_syst_nodes, n_syst_nodes))
    CCb = np.zeros((n_syst_nodes, n_bound_nodes))   # number of columns corresponding to external pressure nodes

    # exponent matrices for air exchange calculations
    n_CCa = np.zeros((n_syst_nodes, n_syst_nodes))   # exponent matrix with n for dp=C*flow**n
    n_CCb = np.zeros((n_syst_nodes, n_bound_nodes))  # exponent matrix with n for dp=C*flow**n

    # flow rate matrix for imposed flow rates
    BB_flow = np.zeros((n_syst_nodes, n_bound_nodes))   # number of columns corresponding to external pressure nodes to which the fans can be connected
    U_flow_indexer = []  # array with necessary data for imposed flow rates

    # fan matrix for calculation pressure gains
    U_fan_indexer = []  # array with necessary data for imposed flow rates

    for j, flow_path in enumerate(flow_paths):
        id_0_name = flow_paths[flow_path]['path'][0]
        id_1_name = flow_paths[flow_path]['path'][1]
        # check that at least one node is inside the system
        id_0_inside = id_0_name in system_nodes_names
        id_1_inside = id_1_name in system_nodes_names
        if not id_0_inside and not id_1_inside:  # both nodes are
            raise ValueError('it is not allowed to connect two external pressure nodes together. Please check you project input file')

        # calculation of kb value
        connection = flow_paths[flow_path]['connection']
        if connection['connection_type'] == 'door':
            kb = connection_functions.door_calculate_kb(section=connection['section'], discharge_coefficient=connection['discharge_coefficient'], opening=1)
            # exchange coefficient before multiplying with flow rate
            value = np.abs(kb ** (1/connection['n']) / rho_ref)
            n_flow = connection['n']
        elif 'grille' in connection['connection_type']:  # outlet or inlet_grille, same equations
            kb = connection_functions.grille_calculate_kb(dp0=connection['dp0'], rho0=connection['rho0'], flow0=connection['flow0'], n=connection['n'], opening=1)
            # exchange coefficient before multiplying with flow rate
            value = np.abs(kb ** (1/connection['n']) / rho_ref)
            # np.sign(dp_flow[j]) * kb * abs(rho_ref * dp_flow[j]) ** connection['n']
            n_flow = connection['n']
        elif 'duct_dtu' in connection['connection_type']:
            # exchange coefficient before multiplying with flow rate
            nominal_flowrate = 50  # no impact if the function is used with type="c_lin"
            value = np.abs(connection_functions.duct_dtu_calculate_dploss(flowrate=nominal_flowrate, rho=rho_ref, section=connection['section'], h_diam=connection['h_diam'], length=connection['length'], coefK=connection['coefK'], dzeta=connection['dzeta'], calc_mode='c_lin'))
            n_flow = 0.5
        elif 'flow' in connection['connection_type']:
            value = 1  # keep 0 values in CCa and CCb since flow rate is calculated in the fan models and imposed directly as FAN flow rates.
                       # value is set in FAN matrix
        elif 'fan' in connection['connection_type']:
            # pass
            value = 1
            n_flow = 0.5
        else:
            pass

        # check if both nodes are in the system or one boundary (either put it in CCa or CCb + diagonal in CCa
        if id_0_inside and id_1_inside:  # connect to external node via CCb
            id_0 = system_nodes_names.index(id_0_name)
            id_1 = system_nodes_names.index(id_1_name)
            if ('flow' not in connection['connection_type']) and ('fan' not in connection['connection_type']):
                CCa[id_0, id_1] = value
                CCa[id_1, id_0] = value
                n_CCa[id_0, id_1] = n_flow
                n_CCa[id_1, id_0] = n_flow
            else:
                assert ValueError('Fans are not supposed to blow between zones inside the buildings but only between boundary conditions and zones')

            flow_paths[flow_path]['flow_matrix'] = 'FFa'
            flow_paths[flow_path]['flow_sign'] = -1
            flow_paths[flow_path]['path_ids'] = [id_1, id_0]

        elif id_0_inside:  # both nodes are in the system, thus only fill in CCa
            flow_sign = 1
            id_0 = system_nodes_names.index(id_0_name)
            id_1 = boundary_nodes_names.index(id_1_name)
            if 'flow' not in connection['connection_type']:
                CCb[id_0, id_1] = value
                n_CCb[id_0, id_1] = n_flow
            else:
                BB_flow[id_0, id_1] = -value  # 1 in case of BB_flow, flow rate of this fan is in the U_flow array
                U_flow_indexer.append([flow_path, id_1, id_1_name, id_0])  # save name of flow path to get directly to the fan model saved in the flow path
            if 'fan' in connection['connection_type']:
                U_fan_indexer.append([flow_path, id_1, id_1_name, id_0, flow_sign])  # save name of flow path to get directly to the fan model saved in the flow path

            flow_paths[flow_path]['flow_matrix'] = 'FFb'
            flow_paths[flow_path]['flow_sign'] = flow_sign
            flow_paths[flow_path]['path_ids'] = [id_0, id_1]

        elif id_1_inside:
            flow_sign = -1
            id_0 = boundary_nodes_names.index(id_0_name)
            id_1 = system_nodes_names.index(id_1_name)
            if 'flow' not in connection['connection_type']:
                CCb[id_1, id_0] = value
                n_CCb[id_1, id_0] = n_flow
            else:
                BB_flow[id_1, id_0] = value  # 1 in case of BB_flow, flow rate of this fan is in the U_flow array
                U_flow_indexer.append([flow_path, id_0, id_0_name, id_1])  # save name of flow path to get directly to the fan model saved in the flow path
            if 'fan' in connection['connection_type']:
                U_fan_indexer.append([flow_path, id_0, id_0_name, id_1, flow_sign])  # save name of flow path to get directly to the fan model saved in the flow path

            flow_paths[flow_path]['flow_matrix'] = 'FFb'
            flow_paths[flow_path]['flow_sign'] = flow_sign
            flow_paths[flow_path]['path_ids'] = [id_1, id_0]

        else:
            pass

    return CCa, CCb, n_CCa, n_CCb, BB_flow, U_flow_indexer, U_fan_indexer


def solve_pressure_system(AA, BB, CCa_act, CCb_act, BB_flow, U_pressure, U_flow, flow_paths, nodes, system_nodes_names):
    """
    # from Mathis
        flow = kb * rho_ref**n * dp**n

    (p1-p0) = 1/rho_ref * kb**(-1/n) * flows**(1/n) // + correction(f(height, T)

    simplified to (p1-p0) = kb**(-1/n) / rho_ref * flows**(1/n) // + correction(f(height, T)
    linearised to :
    (p1-p0) = kb**(-1/n) / rho_ref * flows(it-1)**(1/n-1) * flows // + correction(f(height, T)

    Equation to solve flow balance at each node:
    kb**(-2)*(pj-pi) + injected_flow = 0
    A * P + B * U = 0
    positive pressure difference --> inlet flow (air inlet)
    new for air:
    check all boundary nodes, calculate flowrates by: (pbi - pbj) = kb_i,j**(-2) * flow_i,j(it-1) * flow_i,j(it)
    --> flow_i,j = (pbi - pbj) / kb_i,j**(-2) / flow_i,j(it-1)

    :param AA: flow_resistance_coeff matrix for (nj - ni)
    :param BB: flow_resistance_coeff for (ninj - ni)) + 0 or 1 for flow injection (if exists, in case of hybrid ventilation)
    :param CCa_act: flow resistance coefficient matrix between system nodes
    :param CCb_act: flow resistance coefficient matrix between boundary and system nodes
    :param U: inlet conditions array [inlet pressure, inlet flowrate 1 , inlet flowrate 2,...]

    :return: pressures: pressure array of all system nodes
    :return: flowrates: matrix with flow rates between all system nodes
    :return: flowrates_boundary: matrix with flow rates between all boundary and system nodes

    """

    size_nodes = np.shape(BB)[0]
    size_U = len(U_pressure)
    buoyancy = True
    if buoyancy:
        # initialise matrices for corrective pressure difference due to bouyancy of connection height
        dpressures_aa_buoyancy = np.zeros((size_nodes, size_nodes))  # corrections for flow paths inside system nodes
        dpressures_bb_buoyancy = np.zeros((size_nodes, size_U)) # corrections for flow paths between system nodes and boundary nodes
        for flow_path in flow_paths:
            if 'fan' not in flow_paths[flow_path]['connection']['connection_type']:  # TODO: check with Francois if this effect is considfered in the fan flow calculation
                name_from = flow_paths[flow_path]['path'][0]
                name_to = flow_paths[flow_path]['path'][1]
                index_from = flow_paths[flow_path]['path_ids'][0]
                index_to = flow_paths[flow_path]['path_ids'][1]
                # calculate pressure correction value to apply later in the matrix calculation
                rho_from = p_ref / (Rs_air * (t_ref_K + nodes[name_from]['temperature']))
                rho_to = p_ref / (Rs_air * (t_ref_K + nodes[name_to]['temperature']))
                # adding buoyancy term to pressure flow
                delta_p = - (rho_from - rho_to) * g * flow_paths[flow_path]['z']
                # fill in the matrices with delta_p
                if flow_paths[flow_path]['flow_matrix'] == 'FFa':  # this is in the CCa matrix with system nodes
                    dpressures_aa_buoyancy[index_from, index_to] = - delta_p
                    dpressures_aa_buoyancy[index_to, index_from] = delta_p
                else:
                    dpressures_bb_buoyancy[index_from, index_to] = delta_p * flow_paths[flow_path]['flow_sign']

        buoyancy_correction = np.sum(dpressures_aa_buoyancy * CCa_act, axis=1) + np.sum(dpressures_bb_buoyancy * CCb_act, axis=1)
        buoyancy_correction = np.reshape(buoyancy_correction, (size_nodes, 1))

        pressures = np.dot(-inv(AA), np.dot(BB, U_pressure) - buoyancy_correction + np.dot(BB_flow, U_flow))

        flowrates = pressures * CCa_act - \
                    np.reshape(pressures, (1, size_nodes)) * CCa_act + \
                    dpressures_aa_buoyancy * CCa_act
        # flowrate = flow1 + flow2 + flow3
        # flow1 : entering air flow due to pressure difference between nodes, via connections (openings etc.)
        # flow2 : leaving air flow due to pressure difference between nodes, via connections (openings etc.)
        # flow3 : air flow due to pressure correction of connection heights

        flowrates_boundary = pressures * CCb_act - \
                             np.reshape(U_pressure, (1, size_U)) * CCb_act + \
                             dpressures_bb_buoyancy * CCb_act  + \
                             np.reshape(U_flow, (1, size_U)) * BB_flow
        # flowrate = flow1 + flow2 + flow3
        # flow1 : entering air flow due to pressure difference between nodes and boundary nodes via connections (openings etc.)
        # flow1 : leaving air flow due to pressure difference between nodes and boundary nodes via connections (openings etc.)
        # flow3 : air flow due to pressure correction of connection heights


    else:
        # # solve pressure system
        pressures = np.dot(-inv(AA), np.dot(BB, U_pressure) + np.dot(BB_flow, U_flow))
        # # calculate flow rates
        flowrates = pressures * CCa_act - \
                    np.reshape(pressures, (1, size_nodes)) * CCa_act
        flowrates_boundary = pressures * CCb_act - \
                             np.reshape(U_pressure, (1, size_U)) * CCb_act + \
                             np.reshape(U_flow, (1, size_U)) * BB_flow

    return pressures, flowrates, flowrates_boundary


def gen_pressure_system(CTa, CTb, FFa_act, FFb_act, CCa, CCb, n_CCa, n_CCb):
    """
    Generate CC matrix with pressure drop coefficients (used later to construct A matrix of pressure system)
    :param CTa: Connectivity table between system nodes (i : inlet, j : outlet)
    :param CTb: Connectivity table between boundary and system nodes (i : inlet, j : outlet)
    :param FFa_act: Current Flow rate matrix between system nodes
    :param FFb_act: Current Flow rate matrix between boundary and system nodes
    :param CCa: flow resistance coefficient matrix between system nodes
    :param CCb: flow resistance coefficient matrix between boundary and system nodes

    :return: CCa_act: flow resistance coefficient matrix between system nodes
    :return: CCb_act: flow resistance coefficient matrix between boundary and system nodes

    """
    CCa_act = copy.deepcopy(CCa)
    CCb_act = copy.deepcopy(CCb)

    for connection in CTa:  # go through connectivity table (avoid check for zeros at each time)
        flowrate = np.abs(FFa_act[connection[0], connection[1]])
        flowrate = max(abs(flowrate), 1e-3)
        # dp = C * flow ^ (1/n)
        # changed to: dp = C_act * flow
        # with C_act = C*flow ** (1/n-1)
        n = n_CCa[connection[0], connection[1]]
        # calculate the pressure drop coefficients. For a segment, dp = C * flow ^ (1/n)
        CCa_act[connection[0], connection[1]] /= flowrate**(1/n-1)

    for connection in CTb:  # go through connectivity table (avoid check for zeros at each time)
        flowrate = np.abs(FFb_act[connection[0], connection[1]])
        flowrate = max(abs(flowrate), 1e-3)
        n = n_CCb[connection[0], connection[1]]
        # calculate the pressure drop coefficients. For a segment, dp = C * flow ^ (1/n)
        CCb_act[connection[0], connection[1]] /= flowrate**(1/n-1)

    return CCa_act, CCb_act


def generate_AA_BB_pressure_system(U_pressure, U_flow, CCa_act, CCb_act, BB_flow, flow_paths, nodes, system_nodes_names):
    """
    Generate A and B matrices to solve the pressure system : AP + BU = 0

    :param U: fan flowrates and boundary pressures
    :param CCa_act: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment resistance flow coefficients
    :param nnodes: number of nodes in the network
    :param fan_list: list of [j, i] nodes for fan location
    :param inlet_pressure_ids: list of external pressure nodes

    :return: pressures: pressure array of all system nodes
    :return: flowrates: matrix with flow rates between all system nodes
    :return: flowrates_boundary: matrix with flow rates between all boundary and system nodes

    """

    ######################
    # generate AA matrix
    AA = copy.deepcopy(CCa_act)
    BB = copy.deepcopy(CCb_act)

    # set diagonal of AA
    for i, column in enumerate(CCa_act):  # leaving pressure potential go through columns
        AA[i, i] = -np.sum(column) - np.sum(BB[i, :])

    ######################

    pressures, flowrates, flowrates_boundary = solve_pressure_system(AA, BB, CCa_act, CCb_act, BB_flow, U_pressure, U_flow, flow_paths, nodes, system_nodes_names)

    return flowrates, flowrates_boundary, pressures
