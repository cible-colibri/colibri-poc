import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import inv
from models.thermal.vnat.example_hydronics_peter.constants import p_visc


def balancing(balancing_valve_position_list, substation_flowrate_nominal, substation_flowrate_actual,
              pressure_drop_actual_sub, pressure_drop_till_sub, KVs, KV0):
    """
    function that allows the hydronic balancing of all substation loops

    :param balancing_valve_position_list:
    :param substation_flowrate_nominal:
    :param substation_flowrate_actual:
    :param pressure_drop_actual_sub:
    :param pressure_drop_till_sub:
    :return:
    """
    flows_b_norm = substation_flowrate_actual / substation_flowrate_nominal  # current relative flow rate in substation
    flows_b_norm = flows_b_norm/np.max(flows_b_norm)  # normalise with highest of all substations  #TODO: correct when no flows everywhere
    # garder rapport entre sous-stations même quand pompe pas suffisante
    pos_min = 0.01  # minimum position of balancing valve
    dpos_min = 1e-3  # minimum change of valve position during balancing
    dpos_max = 0.1  # maximum change in valve position during balancing
    v_toturn = np.where(flows_b_norm == max(flows_b_norm))[0] # identify loop with highest flow rate (close progressively)
    if len(v_toturn) == 0:
        pass
    else:  # if result is empty
        # before
        v_toturn = v_toturn[0]  # first valve in list
        flow_toturn = flows_b_norm[v_toturn]
        dpos = np.max([dpos_max * (1 - flow_toturn)**2, dpos_min])  # function to reduce valve position
        balancing_valve_position_list[v_toturn] = max([balancing_valve_position_list[v_toturn] - dpos, pos_min])  # apply valve position that has changed (only 1)

        # new one
        # pressure_drop_actual_sub
        # pressure_drop_till_sub
        # dp_2_correct = (pressure_drop_actual_sub + (np.max(pressure_drop_till_sub))-pressure_drop_till_sub)  # difference of each valve inlet pressure to lowest inlet valve pressure
        # cv_ideal = dp_2_correct / substation_flowrate_nominal**2
        #
        # pos = 1./cv_ideal * 3.6 * 1e5 / (KV0 + KVs * (1 - KV0 / KVs))
        # pos[cv_ideal==0] = 1.
        # pos[flows_b_norm<1] = 1.

        pos = [0.059174, 1.]
        pos = [0.0591741, 1.]
        pos = [0.05917, 1.]
        # # pos = (pos+balancing_valve_position_list)/2.
        balancing_valve_position_list = np.clip(pos, 0., 1.)
        # # pos[pos == np.max(pos)] = 1.

        if np.max(balancing_valve_position_list) < 1:  # if no valve has a position of 1, increase all proportionally
            balancing_valve_position_list = np.clip(balancing_valve_position_list * 1. / max(balancing_valve_position_list), 0., 1.)
    return balancing_valve_position_list


def valve(position, kvs, kv0, valve_chars='lin'):
    """
    Determine the capacity of the valve Cv for a given position.
    For a valve : dp = flow ^ 2 / Cv

    :param position: valve position
    :param kvs: description of the flow capacity of the valve (open)
    :param kv0: description of the flow capacity of the valve (close)
    :param valve_chars: valve characteristics (linear, exponential)
    :return:
    """

    if valve_chars == 'lin':  # if linear characteristics
        kv = kv0 + kvs * (1 - kv0 / kvs) * position
    elif valve_chars == 'exp':  # exponential valve characteristics
        kv = kv0 * np.exp(np.log(kvs / kv0) * position)

    kv = np.min([np.max([kv, kv0]), 200])  # ensure result higher than kv0 and lower than 200 (big)
    dp_nom = 1e5
    Cv = 1 / dp_nom * (kv / 3.6)  # dp = 1 / C_v * flow ^ 2 (flow in kg / s) = 1 / resistance
    # --> take linearisation of Cv, so dp = 1/Cv * flow(t-1)

    return Cv


def calc_lambda(inlet_temperature, flowrate, diameter_internal, lamb_tube, k, p_visc):
    """

    Calculate new lambda value of tube segment depending on the type of flow (laminar, turbulent, or in between)

    :param inlet_temperature: Inlet temperature of the tube
    :param flowrate: Flow rate in the tube
    :param diameter_internal: Internal diameter of the tube
    :param lamb_tube: Previous lambda of the tube
    :param k: Pipe roughness
    :param p_visc: Array of factors for cubic equation f(temperature) = kinematic viscosity
    :return: new lambda value

    """

    rho = 1000.  # to calculate rho from temperatures, to do for each segmet and temperature ... I would avoid and keep a constant value
    flowrate = abs(flowrate)  # do all calculations for positive value of flow rate
    v_kin = p_visc[0] * inlet_temperature**3 + p_visc[1] * inlet_temperature**2 + p_visc[2] * inlet_temperature + p_visc[3]  # simple polynomial to define cinetic viscosity
    Re = 4. * flowrate / (diameter_internal * np.pi) / (v_kin * rho)  # Reynolds number
    not_converged_lambda = True
    lamb_tube_0 = lamb_tube
    while not_converged_lambda:
        if flowrate > 0:
            if Re < 2320.:  # laminary flow
                lamb_tube = 64. / Re
            elif Re < 2500.:  # transitory flow so interpolate between laminar value and turbulent one (continuous function to avoid oscillation)
                lambada_turb = (1. / (2. * np.log10(2.51 / (Re * lamb_tube ** 0.5) + k / (3.71 * diameter_internal)))) ** 2
                lambada_lam = 64. / Re
                lamb_tube = lambada_lam + (lambada_turb - lambada_lam) * (Re - 2320) / (2500.-2320.)
            else:  # turbulent flow with colebrook equation
                lamb_tube = (1. / (2. * np.log10(2.51 / (Re * lamb_tube ** 0.5) + k / (3.71 * diameter_internal)))) ** 2
        else:  # keep last lamb_tube
            pass
        delta_lambda = (lamb_tube-lamb_tube_0)/lamb_tube
        if delta_lambda < 1e-9:
            not_converged_lambda = False
        else:
            lamb_tube_0 = lamb_tube

    return lamb_tube


def calc_pressure_drop(lamb_tube, diameter_internal, flowrate):
    """
    function to calculate the pressure drop in a tube segment  based on the flow rate

    :param lamb_tube: Lambda value of the tube
    :param diameter_internal: Internal diameter of the tube
    :param flowrate: Flow rate in the tube
    :return:
    """

    rho = 1000.  # to calculate rho from temperatures, to do for each segmet and temperature ... I would avoid and keep a constant value
    flowrate = abs(flowrate)  # do all calculations for positive value of flow rate
    velocity = flowrate / rho / (diameter_internal**2 / 4. * np.pi)  # calculate velocity from flow rate in kg/s
    pressure_drop_m = lamb_tube * rho * velocity**2 / (2.*diameter_internal)  # pressure drop in [Pa]

    return pressure_drop_m, velocity


def solve_pressure_system(AA, BB, CC, U):
    """
    (p1-p0) = clin * flows**2
    linearised to :
    (p1-p0) = clin * flows(t-1) * flows

    Equation to solve flow balance at each node:
    clin*(pj-pi) + injected_flow = 0
    A * P + B * U = 0
    positive pressure difference --> inlet flow (pump)
    negative pressure difference --> substation

    :param AA: flow_resistance_coeff matrix for (nj - ni)
    :param BB: flow_resistance_coeff for (ninj - ni))
    :param CC: valve flow coefficient matrix
    :param U: inlet conditions array [inlet pressure, inlet flowrate 1 , inlet flowrate 2,...]
    :return:
    """

    P = np.zeros((len(AA), 1))
    # solve system
    P = np.dot(-inv(AA), np.dot(BB, U))
    # flow rates
    flowrate = P * CC - np.reshape(P, (1, len(P))) * CC

    return P, flowrate


def size_tubes(MAT, CT, DD, LL, SSH, FF, T, LAMB, p_visc, tube_base, niter, sizing_method=['velocity','ideal',0.67]):
    """
    function to size tubes based on velocity or pressure drop

    :param MAT: Material matrix (0=iron, 1=copper, 2=pehd)
    :param CT: Connectivity table (i : inlet, j : outlet)
    :param DD: Diameter matrix
    :param LL: Length matrix
    :param SSH: Singular pressure drop share matrix
    :param FF: Flow rate matrix
    :param T: Temperature array for each node
    :param LAMB: Lambda matrix (friction coefficients)
    :param p_visc: Array of factors for cubic equation f(temperature) = kinematic viscosity
    :param tube_base: characteristics of tube for each material
    :param sizing_method: ['velocity',value] for velocity threshold
                          ['pressure_drop',value] for pressure drop/m threshold
    :return: DD, Diameter matrix with the adapted values

    """

    sizing_type = sizing_method[0]
    search_type = sizing_method[1]
    threshold = sizing_method[2]
    rho = 1000.  # to calculate rho from temperatures, to do for each segmet and temperature ... I would avoid and keep a constant value

    for connection in CT:  # go through connectivity table (avoid check for zeros at each time
        # load all characteristcs for the current segment
        material = MAT[connection[0], connection[1]]
        inlet_temperature = T[connection[0]]
        flowrate = np.abs(FF[connection[0], connection[1]])
        diameter_internal = DD[connection[0], connection[1]]
        pipe_length = LL[connection[0], connection[1]]
        lamb_tube = LAMB[connection[0], connection[1]]
        singular_share = SSH[connection[0], connection[1]]
        k = tube_base['pipe_roughness'][material]
        Dlist = tube_base['diameter_internal'][material]

        if sizing_type == 'velocity':
            # velocity = flowrate / rho / (DD ** 2 / 4. * np.pi)  # calculate velocity from flow rate in kg/s
            # flow_rate[m3/s] = D^2 / 4 * pi * vel
            section = flowrate/rho / threshold  # ideal tube section at threshold
            diameter_ideal = np.max([(4.*section/np.pi)**0.5, 0.01])   # do not allow smaller than 10mm
            if search_type == 'ideal':  # just take the "optimal section and diameter"
                diameter_internal = diameter_ideal
            else:  # iterate to identify from data base
                where = np.argwhere(Dlist > diameter_ideal)
                if len(where) > 0:
                    diameter_internal = Dlist[where[0]]  # take first in list (just higher than optimal section)
                else:
                    diameter_internal = Dlist[-1]  # take the biggest tube

        elif sizing_type == 'pressure_drop':  # this is more tricky, but let's go
            if search_type == 'ideal':  # I didn't want to spend time on this and it is COMPLICATED
                raise ValueError('inlet_the ideal method for tube sizing based on pressure drop is not implemented. Choose data base method')
            else:
                not_found = True
                diameter_last = diameter_internal
                pressure_drop_last = threshold
                while not_found:
                    lamb_tube = calc_lambda(inlet_temperature, flowrate, diameter_internal, lamb_tube, k, p_visc)  # calculate lambda function for tube pressure drop calculation
                    pressure_drop_m, velocity = calc_pressure_drop(lamb_tube, diameter_internal, flowrate)  # calculate pressure drop in segment [Pa/m]
                    pressure_drop_m_total = pressure_drop_m / (1. - singular_share)  # from Pa/m to Pa/segment  # calculate pressure drop for whole length and with singular resistances
                    if pressure_drop_m_total > threshold:  # increase tube diameter
                        where = np.argwhere(Dlist > diameter_internal)  # look which one fits
                        if len(where) > 0:
                            diameter_internal = Dlist[where[0]]  # take next bigger one
                        else:
                            diameter_internal = Dlist[-1]  # if not take the biggest one
                        # print('too small')
                    if pressure_drop_m_total < threshold:  # pressure drop is lower than threshold
                        where = np.argwhere(Dlist < diameter_internal)  # check which one fits
                        if len(where) > 0:
                            diameter_internal = Dlist[where[-1]]  # take the smaller one in the data base
                        else:
                            diameter_internal = Dlist[0]  # if not take the biggest one
                        # print('too big',where)

                    # print(diameter_internal,connection, 'search section')
                    # if this or previous iteration below threshold take the one which is/was below
                    if (diameter_internal == Dlist[0]) or (diameter_internal == Dlist[-1]):
                        not_found = False  # tell the whiler to leave loop
                    elif (pressure_drop_m_total < threshold and pressure_drop_last > threshold) or (pressure_drop_m_total > threshold and pressure_drop_last < threshold):
                        if (pressure_drop_last > threshold):  # it was the last one, take the last diameter
                            diameter_internal = diameter_last
                        not_found = False  # tell the whiler to leave loop
                    else:  # set values as "last" for next iteration
                        pressure_drop_last = pressure_drop_m_total
                        diameter_last = diameter_internal
        else:
            raise ValueError('This tube sizing method does not exist! Choose (a) velocity or (b) pressure_drop')

            # apply diameter in the symmetric matrix ((i,j) and (j,i))
        DD[connection[0], connection[1]] = diameter_internal
        DD[connection[1], connection[0]] = diameter_internal
        LAMB[connection[0], connection[1]] = lamb_tube
        LAMB[connection[0], connection[1]] = lamb_tube

    return DD,LAMB


def gen_pressure_system(DD, SSH, LL, MAT, CT, FF, T, LAMB, CC, balancing_valve_position_list, KVs, KV0,
                        substation_list, tube_base):
    """
    Generate CC matrix with pressure drop coefficients (used later to construct A matrix of pressure system)

    :param DD: Diameter matrix
    :param SSH: Singular pressure drop share matrix
    :param LL: Length matrix
    :param MAT: Material matrix (0=iron, 1=copper, 2=pehd)
    :param CT: Connectivity table (i : inlet, j : outlet)
    :param FF: Flow rate matrix
    :param T: Temperature array for each node
    :param LAMB: Lambda matrix (friction coefficients)
    :param CC: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment flow resistance coefficients
    :param run_balancing:
    :param balancing_valve_position_list:
    :param KVs: valve coefficient when open for each substation
    :param KV0: valve coefficient when closed for each substation
    :param substation_list: List of substation in the network
    :param nnodes: number of nodes (unused)
    :param tube_base: characteristics of the tube per type of material
    :return:
    """

    for connection in CT:  # go through connectivity table (avoid check for zeros at each time
        # load data for segment (could be a function since used twice (here and in the tube sizing function)
        material = MAT[connection[0], connection[1]]
        k = tube_base['pipe_roughness'][material]
        inlet_temperature = T[connection[0]]
        flowrate = FF[connection[0],connection[1]]
        diameter_internal = DD[connection[0], connection[1]]
        pipe_length = LL[connection[0], connection[1]]
        lamb_tube = LAMB[connection[0], connection[1]]
        singular_share = SSH[connection[0], connection[1]]

        # calculate segment lambda
        lamb_tube = calc_lambda(inlet_temperature, flowrate, diameter_internal, lamb_tube, k, p_visc)  # calculate lambda function for tube pressure drop calculation
        pressure_drop, velocity = calc_pressure_drop(lamb_tube, diameter_internal, flowrate)  # calculate pressure drop in segment [Pa/m]
        pressure_drop *= pipe_length / (1.-singular_share)  # from Pa/m to Pa/segment (calculate pressure drop for whole length and with singular resistances)
        LAMB[connection[0], connection[1]] = lamb_tube
        LAMB[connection[1], connection[0]] = lamb_tube

        # calculate the pressure drop coefficients. For a segment, dp = C * flow ^ 2
        CC[connection[0], connection[1]] = np.abs(flowrate/pressure_drop)
        CC[connection[1], connection[0]] = np.abs(flowrate/pressure_drop)  # same on the other side of the diagonal
        CC[np.isnan(CC)] = 1e-10  # if flow rate is 0 this one gives nan (this can really happen)

    for i, sub in enumerate(substation_list):
        kvs = KVs[i]
        kv0 = KV0[i]
        valve_position = balancing_valve_position_list[i]
        cv = valve(valve_position, kvs, kv0, valve_chars='lin')  # has to be nominal flowrate as input!!! (characteristic flow coefficient of the valve)
        # CC[sub[0], sub[1]] = 1. / (1. / CC[sub[0], sub[1]] + 1. / cv)  # 1 / (1/c + 1/cv)
        CC[sub[0], sub[1]] = 1. / (1. / cv)  # 1 / (1/c + 1/cv)
        CC[sub[1], sub[0]] = CC[sub[0], sub[1]]

    return CC, LAMB


def generate_AA_BB_pressure_system(U, CC, nnodes, pump_list):
    """
    Generate A and B matrices to solve the pressure system : AP + BU = 0

    :param U: pump flowrate
    :param CC: flow resistance coefficient matrix, composed of the valve flow resistance coefficients and segment resistance flow coefficients
    :param nnodes: number of nodes in the network
    :param pump_list: list of [j, i] nodes for pump location
    :return:
    """

    ######################
    # generate AA matrix

    # AA = np.zeros((nnodes, nnodes))
    # for i, row in enumerate(CC):  # entering pressure potential go through columns
    #     AA[i, :] = row
    AA = CC.copy()

    ######################
    # set BB matrix

    BB = np.zeros((nnodes, len(pump_list)+1))  # [pin1, ..., pinn, flow_1, ..., flown]
    BB[pump_list[0][0], 0] = 1.  # impose return pressure at main station
    for i, pump in enumerate(pump_list):  # link inlet flow rates from pump calculation
        BB[pump[0], i + 1] = -1.  # link inlet flow rate
        BB[pump[1], i + 1] = 1.  # link inlet flow rate

    ######################
    # set diagonal of AA

    for i, column in enumerate(CC):  # leaving pressure potential go through columns
        AA[i, i] = -np.sum(column) - np.sum(BB[i, 0])  # np.sum(BB[i, 0:len(inj_nodes)])

    P, FF = solve_pressure_system(AA, BB, CC, U)

    return FF,P


def calc_velocity(CT, FF, DD):
    """
    Calculate the flow velocity

    :param CT: connection table
    :param FF: Flow rate matrix
    :param DD: Diameter matrix
    :return:
    """

    VEL = np.zeros((len(FF), len(FF)))
    for con in CT:
        if FF[con[0], con[1]] > 0:
            velocity = np.abs(FF[con[0], con[1]] / 1000. / (DD[con[0], con[1]]**2 / 4. * np.pi))  # calculate velocity from flow rate in kg/s
            VEL[con[0], con[1]] = velocity
            VEL[con[1], con[0]] = velocity
    return VEL


def calc_tube(diameter_internal, tube_length, inlet_temperature, flowrate, lambada, k, share_singular=0.5):
    lambada = calc_lambda(inlet_temperature, flowrate, diameter_internal, lambada, k, p_visc)  # calculate lambda function for tube pressure drop calculation
    pressure_drop,velocity = calc_pressure_drop(lambada,diameter_internal,flowrate)
    pressure_drop *= tube_length * (1-share_singular)# from Pa/m to Pa/segment  # calculate tube resistance
    return pressure_drop, lambada, velocity


def print_results(flowrate, P, P0, flow_paths, flows=True):
    if flows:
        # plot results
        for i in flow_paths:
            print('path (', i[0], '-', i[1], ') - Flow rate: ', np.round(flowrate[i[0], i[1]]*3.6, 3), 'm3/h')
    for i in range(len(P)):
        print("Node {:1} pressure: {:10.2f} [Pa] - delta {:5.2f}".format(i, P[i, 0], P[i, 0] - P0[i, 0]))


def plot_grid(P, FF, VEL, DD, LL, nodes, flow_paths, pump_list, substation_list, plot='flow'):
    col_vec = ['r', 'b', 'y']
    plt.figure()

    for node in nodes:
        plt.text(node[1] + 0.01, node[2] + 0.01, '(' + str(node[0]) + ') ' + str(int(P[node[0]]/1e5)) + ' kP')#, Fontsize=7)

    for path in flow_paths:
        first_node = nodes[path[0]][1:3]  # coordinates from first node
        sec_node = nodes[path[1]][1:3]    # coordinates from second node
        plt.plot([first_node[0], sec_node[0]], [first_node[1], sec_node[1]], col_vec[path[2]])  # plot segment
        x_seg = np.mean([first_node[0], sec_node[0]])  # x position in the middle of both nodes
        y_seg = np.mean([first_node[1], sec_node[1]])  # y position in the middle of both nodes
        sign_dp = P[nodes[path[0]][0]] > P[nodes[path[1]][0]]  # sign of pressure difference
        if first_node[0] == sec_node[0]:  # the segment is a vertical line
            if first_node[1] > sec_node[1]:  # normal flow direction is DOWN
                if sign_dp:  # flow is in normal direction
                    dx = [0., 0.02]
                    dy = [-0.02, 0.]
                else:
                    dx = [0., -0.02]
                    dy = [0., -0.02]
            else:  # normal flow is UP
                if sign_dp:  # flow is in normal direction
                    dx = [0., -0.02]
                    dy = [0., -0.02]
                else:
                    dx = [0., 0.02]
                    dy = [-0.02, 0.]
        else:  # horizontal line
            if sec_node[0] > first_node[0]:  # normal flow direction is LEFT-->RIGHT
                if sign_dp:  # flow is in normal direction
                    dx = [0., -0.02]
                    dy = [0., -0.02]
                else:
                    dx = [-0.02, 0.]
                    dy = [0., -0.02]
            else:  # normal flow is UP
                if sign_dp:  # flow is in normal direction
                    dx = [-0.02, 0.]
                    dy = [0., -0.02]
                else:
                    dx = [0., -0.02]
                    dy = [0., -0.02]

        plt.plot([x_seg + dx[0], x_seg + dx[1]], [y_seg + dy[0], y_seg + dy[1]], col_vec[path[2]])  # plot arrows

        if plot == 'flowrate':
            values = FF*3.6
            unit = 'm3/h'
            title = 'Flow rates'
        elif plot == 'velocity':
            values = VEL
            unit = 'm/s'
            title = 'Fluid velocities'
        elif plot == 'diameter':
            values = DD*1000.
            unit = 'mm'
            title = 'Tube diameters'
        elif plot == 'length':
            values = LL
            unit = 'm'
            title = 'Tube lengths'
        else:
            raise ValueError('plot type not implemented. Use flow, velocity or diameter')

        plt.text(np.mean([first_node[0], sec_node[0]])+0.02, np.mean([first_node[1], sec_node[1]]) - 0.03,
                 str(np.abs(np.round(values[path[0], path[1]], 2))) + unit)#, Fontsize=7)  # plot flow rates

        for i, sub in enumerate(substation_list):
            a = nodes[sub[0]][1:3]
            b = nodes[sub[1]][1:3]
            plt.plot([a[0], b[0]], [a[1], b[1]], 'grey')#, Linewidth=0.1)
            if a[0] - a[1] == 0:  # horizontal line
                plt.text(np.mean([a[0], b[0]]) - 0.05, np.mean([a[1], b[1]]) - 0.05, 'Sub'+str(i))
            else:
                plt.text(np.mean([a[0], b[0]]) + 0.05, np.mean([a[1], b[1]]) - 0.05, 'Sub'+str(i))
        for i, p in enumerate(pump_list):
            a = nodes[p[0]][1:3]
            b = nodes[p[1]][1:3]
            plt.plot([a[0], b[0]], [a[1], b[1]], 'g')#, Linewidth=2)
            if a[0] - a[1] == 0:  # horizontal line
                plt.text(np.mean([a[0], b[0]]) - 0.05, np.mean([a[1], b[1]]) - 0.05, 'Gen'+str(i))
            else:
                plt.text(np.mean([a[0], b[0]]) + 0.02, np.mean([a[1], b[1]]) - 0.02, 'Gen'+str(i))
        plt.title(title)
        plt.axis('OFF')
    # plt.show()


def plot_convergence(deltasq):
    # convergence plot
    plt.figure()
    plt.plot(deltasq, 'go-')
    plt.xlabel('Iteration step')
    plt.ylabel('Average relative pressure change from last iteration')
    plt.title('Convergence plot')
    # plt.ylim([0.,100.])
