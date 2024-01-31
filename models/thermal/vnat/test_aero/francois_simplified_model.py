import numpy as np
import time
# from vnat.test_cases.data_model import flow_paths, nodes, rho_ref, t_ref, model, t_ext
from vnat.test_cases.data_model import rho_ref, t_ref, t_ext
from scipy import optimize
from vnat.test_aero.models import bilan_total
import math


def simplified_model(t_final, nodes_init, flow_paths_init, model, apply_dp, dynamic_test):

    flow_paths = flow_paths_init.copy()
    nodes = nodes_init.copy()

    # initialization of main unknown variables
    n_pressure = 0
    n_special=0
    for i in nodes:
        if nodes[i]['type'] == 'node':
            n_pressure = n_pressure + 1
    for j in flow_paths:
        connection = flow_paths[j]['connection']
        if (connection['connection_type'] == 'fan_mechanical'
              or connection['connection_type'] == 'duct_dtu'):
            n_special=n_special+1
    # time loop
    t = 0
    dt = 1
    # t_final = 168 #8759
    x0 = np.zeros(n_pressure+n_special)
    flowrate_results = np.zeros((t_final, len(flow_paths)))
    pressure_results = np.zeros((t_final, n_pressure))

    while t < t_final:

        for node in nodes:
            if nodes[node]['type'] == 'boundary_condition':
                nodes[node]['pressure'] = nodes[node]['pressure_list'][t]
                # buoyant rho  with boussinesq linear approximation
                # rhobound=rho_ref * (1 - (nodes[i]['temperature']-t_ref)/(t_ref+273.15))
                # rhoext=rho_ref * (1 - (t_ext-t_ref)/(t_ref+273.15))
                # buoyant rho with exact calculation using perfect gaz law (same as Mathis)
                rhobound = 101300 / (287 * (273.15 + nodes[node]['temperature']))
                rhoext = 101300 / (287 * (273.15 + t_ext))
                # pressure correction
                nodes[node]['pressure'] -= (rhoext-rhobound)*9.81*nodes[node]['z']
        # calculate internal pressures
        x = optimize.fsolve(bilan_total, x0, args=(n_pressure, nodes, n_special, flow_paths, rho_ref, t_ref), xtol=1.e-7)

        # set results of current time step
        k = 0
        for i in nodes:
            if nodes[i]['type'] == 'node':  # pressure set at node level for output
                # buoyant rho  with boussinesq linear approximation
                #rhonode=rho_ref * (1 - (nodes[i]['temperature']-t_ref)/(t_ref+273.15))
                #rhoext=rho_ref * (1 - (t_ext-t_ref)/(t_ref+273.15))
                # buoyant rho with exact calculation using perfect gaz law (same as Mathis)
                rhonode = 101300 / (287 * (273.15 + nodes[i]['temperature']))
                rhoext = 101300 / (287 * (273.15 + t_ext))
                # pressure correction
                pressure_results[t, k] = x[k] + (rhoext-rhonode)*9.81*nodes[i]['z']
                k = k+1

        flowrate_results[t, :] = bilan_total(x, n_pressure, nodes, n_special, flow_paths, rho_ref, t_ref, calc_type='flow_calc') * 3600 / rho_ref

        x0 = x  # keep last pressure vector for next time step
        t = t + dt  # go to next time step

    # print('Dp : ', x)

    mode_papoter = False
    if mode_papoter:
        print('Mathis results:')
        print('Mathis pressures: ', pressure_results[-1, :])
        print('Mathis flow rates: ', flowrate_results[-1, :])
        print('CPUtime Mathis simplified : ', toc - tic)

    for j, flow_path in enumerate(flow_paths):
        flow_paths[flow_path]['flow_rate_simplified'] = flowrate_results[:, j]

# if __name__ == '__main__':
#     test_main()
