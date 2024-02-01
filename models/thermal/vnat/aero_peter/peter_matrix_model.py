import numpy as np
import copy
import math
import time
from models.thermal.vnat.test_cases.data_model import rho_ref, t_ext, t_ref, p_ref, Rs_air, t_ref_K, g
from models.thermal.vnat.aero_peter.utilities_peter_matrix import construct_nodes_sep, check_compatibility, \
    construct_CCi, gen_pressure_system, generate_AA_BB_pressure_system
import models.thermal.vnat.test_aero.connection_functions as cf


def matrix_model(t_final, nodes, flow_paths, model, apply_dp, dynamic_test):

    # define boundary and system pressure nodes
    boundary_nodes_ids, boundary_nodes_names, boundary_nodes_pressure, system_nodes_names, system_nodes_ids = construct_nodes_sep(nodes)

    # matrix with coefficients (kb values)
    CCa, CCb, n_CCa, n_CCb, BB_flow, U_flow_indexer, U_fan_indexer = construct_CCi(flow_paths, boundary_nodes_names, system_nodes_names)

    # check if all is connected as it should
    fan_suction_nodes = check_compatibility(boundary_nodes_names, flow_paths)

    # connectivity table
    CTa = np.argwhere(np.abs(CCa) > 1e-30)  # connectivity table to act like in sparse ...
    CTb = np.argwhere(np.abs(CCb) > 1e-30)  # connectivity table to act like in sparse ...

    # initialise flow matrix
    n_syst_nodes = len(system_nodes_ids)
    n_bound_nodes = len(boundary_nodes_ids)
    nominal_flowrate = 10./3600. * rho_ref  # any value, juste for initialising
    # initialise 2 flow matrices:
    FFa = np.ones((n_syst_nodes, n_syst_nodes)) * nominal_flowrate  # initial flow rate is nominal one in all segments
    FFb = np.ones((n_syst_nodes, n_bound_nodes)) * nominal_flowrate  # initial flow rate is nominal one in all segments
    # initialise 2 current flow matrices (for relaxation):
    FFa_act = np.ones((n_syst_nodes, n_syst_nodes)) * nominal_flowrate  # initial flow rate is nominal one in all segments
    FFb_act = np.ones((n_syst_nodes, n_bound_nodes)) * nominal_flowrate  # initial flow rate is nominal one in all segments

    # initial states of Network
    pressures = np.zeros(n_syst_nodes)             # initial node pressures to 0
    pressures_last = np.zeros(n_syst_nodes) + 20.  # set a different pressure for previous time step

    # initialise results
    pressure_results = np.zeros((t_final, n_syst_nodes))

    # boudary connection arrays
    U_pressure = np.zeros((int(n_bound_nodes), 1))  # n pressure nodes in boundary
    U_flow = np.zeros((n_bound_nodes, 1))  # n injection nodes for flow rate by fans

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Simulation loop
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # print('---------------------- Simulation loop -----------------------------------------')
    iter_max = 100
    for t in range(t_final):
        not_converged_step = True
        niter = 0

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Iteration step
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        while not_converged_step:  # iteration loop on sizing of tube sections

            if niter >= iter_max:
                print('step : ', t, 'number of iterations at high limit')

            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # Set boundary condition for current time step
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # U array for boundary conditions - pressure boundary nodes
            i = 0
            for node in nodes:
                if nodes[node]['type'] == 'boundary_condition':
                    dp_corr = 0.  # eventual correction (fan etc.)
                    nodes[node]['pressure'] = nodes[node]['pressure_list'][t]
                    rhobound = p_ref / (Rs_air * (t_ref_K + nodes[node]['temperature']))
                    rhoext = p_ref / (Rs_air * (t_ref_K + t_ext))
                    # pressure correction
                    dp_corr -= (rhoext - rhobound) * g * nodes[node]['z']
                    if node in fan_suction_nodes:
                        for f in range(len(U_fan_indexer)):
                            if node == U_fan_indexer[f][2]:  # this is the right one
                                id_to = U_fan_indexer[f][3]
                                id_from = U_fan_indexer[f][1]
                                connection = flow_paths[U_fan_indexer[f][0]]['connection']
                                flowrate = FFb_act[id_to, id_from]
                                sign = U_fan_indexer[f][4]
                                dp_corr += sign * cf.fan_mechanical_calculate_dploss(flowrate=flowrate * 3600 / rho_ref,
                                                                                     dplaw=connection['pressure_curve'])
                    nodes[node]['pressure'] += dp_corr
                    U_pressure[i, 0] = nodes[node]['pressure']  # set boundary pressures in U_pressure array
                    i += 1

            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # U fan array for boundary conditions - fan flow rates (imposed flow rates in pressure model)
            for flow_i in U_flow_indexer:
                # flow_path = flow_i[0]
                # id_from = flow_i[1]
                # name_from = flow_i[2]
                # id_to = flow_i[3]
                connection = flow_paths[flow_i[0]]['connection']
                flowrate = connection['flow_rate']/3600.
                U_flow[flow_i[1], 0] = flowrate  # TODO: Check for sign !!!


            # CC update using flow rate. Use average flow with relaxation factor
            if niter > 0:
                smoothie = 0.5
                FFa_act = FFa * smoothie + FFa_act * (1-smoothie)
                FFb_act = FFb * smoothie + FFb_act * (1-smoothie)

            # CCa, CCb = update_CCi(CCa, CCb, FFa_act, FFb_act, flow_paths, boundary_nodes_names, system_nodes_names)

            # generate the CCa_act and CCb_act matrices. with : C_act = C * flow_last_it ** (1/n-1)
            CCa_act, CCb_act = gen_pressure_system(CTa, CTb, FFa_act, FFb_act, CCa, CCb, n_CCa, n_CCb)

            # set AA and BB matrices and generate pressure matrix P and new flowrate matrix FF
            FFa, FFb, pressures = generate_AA_BB_pressure_system(U_pressure, U_flow, CCa_act, CCb_act, BB_flow, flow_paths, nodes, system_nodes_names)

            # check for difference from last time step
            delta_p = np.abs(pressures - pressures_last) / p_ref  # relative change from last iteration compared to reference pressure p_ref
            delta_p_max = np.abs(np.max(delta_p))  # take the maximum difference from all pressure nodes

            # check for convergence
            if (delta_p_max <= 1e-7) or (niter > iter_max):  # convergence if delta < threshold or at n_iter_max
                not_converged_step = False
                break

            pressures_last = pressures  # keep pressure vector for next iteration step
            niter += 1  # increment iteration number

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Results
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # save data as in test Francois
        pressure_results[t, :] = pressures[:, 0]
        # write pressures in nodes dict
        i = 0
        for node in nodes:
            if nodes[node]['type'] != 'boundary_condition':
                if t == 0:
                    nodes[node]['pressure_list'] = np.zeros(t_final)

                nodes[node]['pressure_list'][t] = pressures[i, 0]
                i += 1

        # write results of flow rates in flow_paths dict
        for flow_path in flow_paths:
            if 'fanny' not in flow_paths[flow_path]['connection']['connection_type']:
                if t == 0:
                    flow_paths[flow_path]['flow_rate_matrixcalc'] = np.zeros(t_final)
                sign = flow_paths[flow_path]['flow_sign']
                index_from = flow_paths[flow_path]['path_ids'][0]
                index_to = flow_paths[flow_path]['path_ids'][1]
                if flow_paths[flow_path]['flow_matrix'] == 'FFb':
                    flow_paths[flow_path]['flow_rate_matrixcalc'][t] = sign * FFb[index_from, index_to] * 3600
                else:
                    flow_paths[flow_path]['flow_rate_matrixcalc'][t] = sign * FFa[index_from, index_to] * 3600

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Results
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    mode_papoter = False
    if mode_papoter:
        print('Pressures of system nodes : ', pressure_results[-1, :])
        FFa_m3h = FFa[np.abs(FFa) > 1e-15] * 3600.
        FFb_m3h = FFb[np.abs(FFb) > 1e-15] * 3600.
        print('Flow rates system nodes : ', FFa_m3h)
        print('Flow rates to boundary nodes : ', FFb_m3h)
        print(niter, ' iterations in matrix calculation method')
        print('CPUtime matrix calculation method: ', sim_time)
