import numpy as np
from scipy.linalg import inv
from vnat.test_cases.data_model import flow_paths, nodes
from vnat.test_aero.test_0 import construct_connectivity_matrix
import vnat.test_aero.connection_functions as cf


def construct_nodes(nodes, flow_paths):
    inlet_pressure_values = []
    inlet_pressure_names = []
    system_pressure_names = []
    for i in nodes:
        if nodes[i]['type'] == 'boundary_condition':
            inlet_pressure_values.append(nodes[i]['pressure'])
            inlet_pressure_names.append(i)
        if nodes[i]['type'] == 'node':
            system_pressure_names.append(i)
    return inlet_pressure_values, inlet_pressure_names, system_pressure_names


def construct_CC(flow_paths, nodes, nnodes, inlet_pressure_names, system_pressure_names):
    CC = np.zeros((nnodes, nnodes))
    # dp_flow = np.zeros(len(flow_paths))
    for j, flow_path in enumerate(flow_paths):
        kfrom = flow_paths[flow_path]['path'][0]
        kto = flow_paths[flow_path]['path'][1]
        dp_flow[j] = dp[kfrom]-dp[kto]
        # calcul du kb
        connection = flow_paths[flow_path]['connection']
        if connection['connection_type'] == 'door':
            kb = cf.door_calculate_kb(section=connection['section'], discharge_coefficient=connection['discharge_coefficient'], opening=1)
        else:
            kb = cf.grille_calculate_kb(dp0=connection['dp0'], rho0=connection['rho0'], flow0=connection['flow0'], n=connection['n'], opening=1)
        CC[]



def solve_pressure_system(AA, BB, CC, U):
    """
    (p1-p0) = 1/(kb**n) * flows**2
    simplified to (p1-p0) = kb**(-2) * flows**2
    linearised to :
    (p1-p0) = kb**(-2) * flows(t-1) * flows

    Equation to solve flow balance at each node:
    kb**(-2)*(pj-pi) + injected_flow = 0
    A * P + B * U = 0
    positive pressure difference --> inlet flow (air inlet)
    new for air:
    check all boundary nodes, calculate flowrates by: (pbi - pbj) = kb_i,j**(-2) * flow_i,j(it-1) * flow_i,j(it)
    --> flow_i,j = (pbi - pbj) / kb_i,j**(-2) / flow_i,j(it-1)

    :param AA: flow_resistance_coeff matrix for (nj - ni)
    :param BB: flow_resistance_coeff for (ninj - ni)) + 0 or 1 for flow injection (if exists, in case of hybrid ventilation)
    :param CC: kb coefficient matrix
    :param U: inlet conditions array [inlet pressure, inlet flowrate 1 , inlet flowrate 2,...]
    :return:
    """

    P = np.zeros((len(AA), 1))
    # solve system
    P = np.dot(-inv(AA), np.dot(BB, U))
    # flow rates
    flowrate = P * CC - np.reshape(P, (1, len(P))) * CC

    return P, flowrate


def gen_pressure_system(CT, FF, CC):
    """
    Generate CC matrix with pressure drop coefficients (used later to construct A matrix of pressure system)

    :param CT: Connectivity table (i : inlet, j : outlet)
    :param FF: Flow rate matrix
    :param CC: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment flow resistance coefficients
    """

    for connection in CT:  # go through connectivity table (avoid check for zeros at each time
        flowrate = FF[connection[0], connection[1]]
        pressure_drop = 10.

        # calculate the pressure drop coefficients. For a segment, dp = C * flow ^ 2
        CC[connection[0], connection[1]] = np.abs(flowrate/pressure_drop)
        CC[connection[1], connection[0]] = np.abs(flowrate/pressure_drop)  # same on the other side of the diagonal
        CC[np.isnan(CC)] = 1e-10  # if flow rate is 0 this one gives nan (this can really happen)

    return CC


def generate_AA_BB_pressure_system(U, CC, nnodes, fan_list):
    """
    Generate A and B matrices to solve the pressure system : AP + BU = 0

    :param U: fan flowrates and external pressures
    :param CC: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment resistance flow coefficients
    :param nnodes: number of nodes in the network
    :param fan_list: list of [j, i] nodes for fan location
    :return:
    """

    ######################
    # generate AA matrix
    AA = CC.copy()

    ######################
    # set BB matrix
    BB = np.zeros((nnodes, len(fan_list)+1))  # [pin1, ..., pinn, flow_1, ..., flown]
    if len(fan_list) > 0:
        BB[fan_list[0][0], 0] = 1.  # impose return pressure at main station
        for i, fan in enumerate(fan_list):  # link inlet flow rates from fan calculation
            BB[fan[0], i + 1] = -1.  # link inlet flow rate
            BB[fan[1], i + 1] = 1.  # link inlet flow rate

    ######################
    # set diagonal of AA

    for i, column in enumerate(CC):  # leaving pressure potential go through columns
        AA[i, i] = -np.sum(column) - np.sum(BB[i, 0])  # np.sum(BB[i, 0:len(inj_nodes)])

    P, FF = solve_pressure_system(AA, BB, CC, U)

    return FF,P


# get connectivity matrix
LL = construct_connectivity_matrix(flow_paths, nodes)
nominal_flowrate = 50./3600

# initialise matrices (for sizer)
CT = np.argwhere(np.abs(LL) > 0.01)  # connectivity table to act like in sparse ...
FF = (LL > 0) * nominal_flowrate  # initial flow rate is nominal one in all segments
nnodes = len(nodes)
inlet_pressures, inlet_pressure_names, pressure_names = construct_nodes(nodes, flow_paths)

CC = np.zeros((nnodes, nnodes))

# initial states of Network
T = np.zeros(nnodes) + 20.  # initial segment temperatures
P = np.zeros(nnodes) + 10000.  # initial node pressures
P0 = P + 10000.
base_pressure = P0[0]

# fans
nfans = 0
fan_list = []
fan_flowrate = []

print('---------------------- Simulation loop -----------------------------------------')
iter_max = 100
for ts in range(1):
    not_converged_step = True
    niter = 0
    while not_converged_step:  # iteration loop on sizing of tube sections
        # set U array
        U = np.zeros((int(nfans + 1), 1))  # n injection nodes for flow rate + 1 pressure node at main fan
        U[0, 0] = base_pressure  # inlet pressure
        for i in range(nfans):
            print('???')
            U[i + 1, 0] = fan_flowrate[i]  # inlet flow rate

        # CC update using flow rate
        if ts >= 0:
            CC = gen_pressure_system(CT, FF, CC)

        # set AA and BB matrices and generate pressure matrix P and new flowrate matrix FF
        FF, P = generate_AA_BB_pressure_system(U, CC, nnodes, fan_list)

        niter += 1  # increment iteration number

        # delta_p = np.max(np.abs((P - P0) / np.max([P,1e-5])))
        delta_p = np.zeros((len(P), 1))
        for p in range(len(P)):
            delta_p[p] = np.abs(P[p] - P0[p]) / np.max(P)  # difficult to find a good criteria ...
        delta_p = np.max(delta_p)

        if niter > iter_max:  # convergence if delta < threshold or at n_iter_max
            not_converged_step = False
            # print('---------------------------------------------------------------')
            # print('Number of iteration ', niter)
            break
        P0 = P  # store pressure vector for next iteration step


