import matplotlib.pyplot as plt
import numpy as np
import time
from vnat.test_aero.francois_simplified_model import simplified_model
from vnat.test_aero.francois_mathis_model import pymathis_model
from vnat.test_cases.data_model import set_test
from vnat.test_cases.boundary_conditions import boundary_matrix
from vnat.aero_peter.matrix_aero import P_Model

t_final = 168
plot_flows = True
n_plot_max = 20
plot_pressures = False
# test case choice : 1) basic data sets
model = 3  # from 2 - 5, base test cases
# test case choice : 2) automatically generated data sets
# to generate a new test case: put the number of nodes as string. This will generate the new data set.
# to reuse an already generated test case, put 'load_' in front of the number of nodes : example: 'load_11'
# model = 'load_100'  # generation/load of test case
# model = 'load_7'  # generation/load of test case
apply_disturbance = [25, 0*48]  # in th example [25, 48], step of 25 Pa applied every 48 hours
apply_buoyancy = False  # if False, the test case is isothermal, if True, temperatures of nodes are set randomly
dynamic_test = 1  # vary pressures based on a sinus function

tests = [0, 1, 2]  # list the test cases you want to compare

legend = []
names = ['Peter 0815', 'Francois 3615', 'Pymathis']
sim_time = []

# Generate or load test case
flow_paths, nodes = set_test(model, apply_buoyancy)
# from vnat.test_cases.data_model_coupling_Temp_Press import nodes, flow_paths
boundary_matrix(nodes, t_final, dynamic_test, apply_disturbance)

if 0 in tests:
    # simulation with matrix calculation
    # inlet nodes with pressure
    tic = time.time()
    my_P = P_Model('my_pressure_model')
    my_P.matrix_model_init(t_final, flow_paths, nodes)

    # print('---------------------- Simulation loop -----------------------------------------')
    niter_max = 10
    for t in range(t_final):
        my_P.not_converged_step = True
        niter = 0

        while my_P.not_converged_step:  # iteration loop on sizing of tube sections
            my_P.matrix_model_calc(t, niter)
            my_P.matrix_model_check_convergence(niter, niter_max)
            niter += 1
        my_P.matrix_model_set_results(t)

    # matrix_model(t_final, nodes, flow_paths, model, apply_disturbance, dynamic_test)
    sim_time.append(time.time() - tic)
    legend.append(names[0])
    print('simulation of ' + names[0] + ' finished')

if 1 in tests:
    # simulation using simplified mathis
    tic = time.time()
    simplified_model(t_final, nodes, flow_paths, model, apply_disturbance, dynamic_test)
    sim_time.append(time.time() - tic)
    legend.append(names[1])
    print('simulation of ' + names[0] + ' finished')
if 2 in tests:
    # simulation using pymathis
    tic = time.time()
    pymathis_model(t_final, nodes, flow_paths, model, apply_disturbance, dynamic_test)
    sim_time.append(time.time() - tic)
    legend.append(names[2])
    print('simulation of ' + names[0] + ' finished')

print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('Simulation time : ')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
for i in range(len(tests)):
    if i in tests:
        print('CPUtime - ', "%15s" % names[i] + ':', "%.3f" % sim_time[i] + ' seconds')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

if plot_flows:
    n_plot = 0
    for flow_path in flow_paths:
        if flow_paths[flow_path]['connection']['connection_type'] != 'fan' and n_plot < n_plot_max:
            plt.figure()
            if 0 in tests:
                plt.plot(flow_paths[flow_path]['flow_rate_matrixcalc'], 'b--', alpha=0.7)
            if 1 in tests:
                plt.plot(flow_paths[flow_path]['flow_rate_simplified'], 'r', alpha=0.7)
            if 2 in tests:
                plt.plot(flow_paths[flow_path]['flow_rate_mathis'], 'k--', alpha=0.7)
            plt.title(flow_path + ' - ' + str(flow_paths[flow_path]['path']))
            plt.legend(legend)
            n_plot += 1
    plt.show()

if plot_pressures:
    plt.figure()
    for node in nodes:
        plt.plot(nodes[node]['pressure_list'], 'k')
        plt.title('Pressure results - ', node)
    plt.show()

