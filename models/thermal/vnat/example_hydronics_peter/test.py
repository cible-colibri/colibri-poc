import numpy as np
import matplotlib.pyplot as plt
from models.thermal.vnat.example_hydronics_peter.pressure_functions import print_results, gen_pressure_system, generate_AA_BB_pressure_system, \
    plot_grid, plot_convergence, calc_velocity, balancing, size_tubes
from models.thermal.vnat.example_hydronics_peter.tests import press_tests
from models.thermal.vnat.example_hydronics_peter.pump_functions import pump, pump_chars
from models.thermal.vnat.example_hydronics_peter.constants import tube_base
from models.thermal.vnat.example_hydronics_peter.constants import p_visc


def launch(choice=0, material=0, singular_share=0.5, random_length=False, nominal_flowrate=3./3.6, plot=['velocity'],
           sizing_method=['velocity', 'base', 0.5], sizing_tubes=True, pump_model=False, plot_pump_curves=False):

    # select and load test case from tests.py file
    LL, nnodes, flow_paths, nodes, pump_list, substation_list = press_tests(choice, random_length)

    # set boundary conditions and inlet
    base_pressure = 0.  # the return node is set to 0 Pa
    pump_flowrate = np.ones(len(pump_list)) * nominal_flowrate  # kg/s

    # generate pumps (possibility of using a pump model with pump curve or imposing a flow rate
    npumps = len(pump_list)
    pump_data_table = []
    for i in range(npumps):  # generate table of pump curves
        pump_data_table.append(pump_chars(flowrate_nominal=pump_flowrate[i]))
    pump_power = np.zeros(npumps)
    pump_speed_nominal = 1500.
    pump_speed = np.ones(npumps) * pump_speed_nominal
    pressure_drop = np.ones(npumps)*10000.

    ################### Initialization ########################

    # initialize substation flow rates
    balancing_valve_position_list = np.ones(len(substation_list))  # initialise balancing valves to open
    substation_flowrate_actual = np.zeros(len(substation_list))  # initialise actual flow rate to zero
    substation_flowrate_nominal = np.ones(len(substation_list)) * nominal_flowrate * 0.5  # for testing, nominal flow rate in each substation is half of the nominal flow rate
    pressure_drop_actual_sub = np.zeros(len(substation_list))
    pressure_drop_till_sub = np.zeros(len(substation_list))

    # choice of kv for the valves
    KVs = np.ones(len(substation_list)) * 1. * nominal_flowrate  # very rough approach for kvs of open valve at 1bar dp
    KV0 = KVs * 0.  # estimate for closed valve

    # initialise matrices (for sizer)
    CT = np.argwhere(np.abs(LL) > 0.1)  # connectivity table to act like in sparse ...
    FF = (LL > 0) * nominal_flowrate  # initial flow rate is nominal one in all segments
    DD = (LL > 0) * 0.5  # initial diameter is 0.05m
    SSH = (LL > 0) * singular_share  # part of singular pressure drop share (default 50%)
    LAMB = (LL > 0) * 0.01  # initial value of lambda for pressure drop calculation (Moody diagramm)
    MAT = (LL > 0) * material  # material matrix 0=iron, 1=copper, 2=pehd - material can be defined segment by segment, so a mix is possible
    CC = np.zeros((nnodes, nnodes))

    # initial states of Network
    T = np.zeros(nnodes) + 40.  # initial segment temperatures
    P = np.zeros(nnodes) + 10000.  # initial node pressures
    P0 = P + 10000.
    ################### Other parameters ########################

    # iteration loop
    not_converged_sizing = True
    threshold_balancing = 1e-2
    threshold_sizing = 1e-4
    iter_max = 10000
    iter_max_balance = 1
    deltasq = []

    # other parameters
    plot_pump_curves = False

    if plot_pump_curves:  # the pump curve and system curve can be plotted during simulation
        plt.ion()
        fig = plt.figure()
        ax = []
        ax.append(fig.add_subplot(411))
        ax.append(fig.add_subplot(412))
        ax.append(fig.add_subplot(413))
        ax.append(fig.add_subplot(414))
    else:  # do not plot ...
        ax = [[], [], [], []]
        fig= []

    ################### Sizing loop ########################
    tosize = True
    if tosize:
        niter = 0  # number of iteration is set to 0 at the beginning of each time step
        niter_sizing = 0
        threshold_simulation = 1e-2

        while not_converged_sizing:  # iteration loop on sizing of tube sections
            not_converged_balancing = True
            niter_balancing = 0
            DD, LAMB = size_tubes(MAT, CT, DD, LL, SSH, FF, T, LAMB, p_visc, tube_base, niter, sizing_method)
            niter_sizing += 1
            while not_converged_balancing:  # iteration loop on balancing of flow rates
                niter_balancing += 1
                # set U array
                U = np.zeros((int(npumps + 1), 1))  # n injection nodes for flow rate + 1 pressure node at main pump
                U[0, 0] = base_pressure  # inlet pressure
                for i in range(npumps):
                    U[i+1, 0] = pump_flowrate[i]  # inlet flow rate

                # CC update using flow rate
                CC, LAMB = gen_pressure_system(DD, SSH, LL, MAT, CT, FF, T, LAMB, CC, balancing_valve_position_list,
                                               KVs, KV0, substation_list, tube_base)

                # set AA and BB matrices and generate pressure matrix P and new flowrate matrix FF
                FF, P = generate_AA_BB_pressure_system(U, CC, nnodes, pump_list)

                # pump calculations
                if pump_model:  # in this cas, use the pump model, otherwise the nominal flow rate is imposed
                    for i in range(npumps):
                        pressure_drop[i] = P[pump_list[i][1]] - P[pump_list[i][0]]
                        pump_flowrate[i], pump_power[i], fig, ax[i] = pump(pump_flowrate[i], pressure_drop[i], pump_speed[i], pump_data_table[i], pump_speed_nominal, plot_pump_curves, niter, fig, ax[i], pump_efficiency=0.25)

                # balancing procedure
                balancing_valve_position_list_last = balancing_valve_position_list.copy()  # it might be necessary to check if the positions have stopped changing
                balancing_valve_position_list = balancing(balancing_valve_position_list, substation_flowrate_nominal, substation_flowrate_actual, pressure_drop_actual_sub, pressure_drop_till_sub, KVs, KV0)

                # check if balancing has "converged"
                for i, sub in enumerate(substation_list):
                    substation_flowrate_actual[i] = np.abs(FF[sub[0], sub[1]])
                    pressure_drop_actual_sub[i] = np.abs(P[sub[0]] - P[sub[1]])
                    pressure_drop_till_sub[i] = np.abs(P[0] - np.max([P[sub[0]],P[sub[0]]]))
                flows_b_norm = substation_flowrate_actual / substation_flowrate_nominal  # current relative flow rate in substation
                flows_b_norm = flows_b_norm / np.max(flows_b_norm)  # normalise with highest of all substations  #TODO: correct when no flows everywhere
                delta_flow = np.abs(1. - np.min(flows_b_norm))
                # print balancing results
                print('normalised flows : ', np.round(flows_b_norm,3), ' / delta: ', np.round(delta_flow,2), ' / position: ', np.round(balancing_valve_position_list,3), ' / iter balance: ',niter_balancing)
                print('dp act : ', pressure_drop_actual_sub, 'flowrate act : ', substation_flowrate_actual)
                if niter_balancing >= iter_max_balance or (delta_flow <= threshold_balancing) or np.sum(np.abs(balancing_valve_position_list_last - balancing_valve_position_list)) == 0:
                    # print('stop balancing at iteration: ', niter)
                    not_converged_balancing = False
                niter += 1  # increment iteration number
                # not_converged_balancing = False

            # delta_p = np.max(np.abs((P-P0)/P))  # difficult to find a good criteria ...
            delta_p = np.zeros((len(P), 1))
            for p in range(len(P)):
                delta_p[p] = np.abs(P[p] - P0[p]) / np.max(P)  # difficult to find a good criteria ...
            delta_p = np.max(delta_p)

            deltasq.append(delta_p)   # keep it for convergence plot

            if (delta_p < threshold_simulation) or (niter > iter_max):  # convergence if delta < threshold or at n_iter_max
                not_converged_sizing = False
                print('---------------------------------------------------------------')
                print('Number of iteration ', niter)
                print('iter sizing : ', niter_sizing)
                print('iter balancing : ', niter_balancing)
                print('substation flow rates : ', flows_b_norm)
                print_results(FF, P, P0, flow_paths)
                break
            else:
                P0 = P  # store pressure vector for next iteration step

    # end of simulation
    plot_convergence(deltasq)  # plot convergence
    VEL = calc_velocity(CT, FF, DD)  # calculate velocity in all segments
    for i in plot:  # plot network with diameter, velocity and flow rate
        plot_grid(P, FF, VEL, DD, LL, nodes, flow_paths, pump_list, substation_list, plot=i)
    plt.show()

    print('go to simulation')
    print([i for i in P])
    print('---------------------- Simulation loop -----------------------------------------')
    run_balancing = False
    iter_max = 300
    for ts in range(1):
        not_converged_step = True
        niter = 0
        while not_converged_step:  # iteration loop on sizing of tube sections
            # set U array
            U = np.zeros((int(npumps + 1), 1))  # n injection nodes for flow rate + 1 pressure node at main pump
            U[0, 0] = base_pressure  # inlet pressure
            for i in range(npumps):
                U[i + 1, 0] = pump_flowrate[i]  # inlet flow rate

            # CC update using flow rate
            CC, LAMB = gen_pressure_system(DD, SSH, LL, MAT, CT, FF, T, LAMB, CC, balancing_valve_position_list,
                                           KVs, KV0, substation_list, tube_base)

            # set AA and BB matrices and generate pressure matrix P and new flowrate matrix FF
            FF, P = generate_AA_BB_pressure_system(U, CC, nnodes, pump_list)

            niter += 1  # increment iteration number

            # delta_p = np.max(np.abs((P - P0) / np.max([P,1e-5])))
            delta_p = np.zeros((len(P),1))
            for p in range(len(P)):
                delta_p[p] = np.abs(P[p] - P0[p]) / np.max(P)  # difficult to find a good criteria ...
            delta_p = np.max(delta_p)

            if (delta_p < threshold_sizing) or (niter > iter_max):  # convergence if delta < threshold or at n_iter_max
                not_converged_step = False
                print('---------------------------------------------------------------')
                print('Number of iteration ', niter)
                break
            P0 = P  # store pressure vector for next iteration step
        # VEL = calc_velocity(CT, FF, DD)  # calculate velocity in all segments
        # for i in plot:  # plot network with diameter, velocity and flow rate
        #     plot_grid(P, FF, VEL, DD, LL, nodes, flow_paths, pump_list, substation_list, plot=i)
        # plt.show()
        #print([i for i in P])

# launch test
# choose sizing method.
# - velocity
#   - ideal: tube section is ideal
#   - base: tube section from base
#   plus : maximum velocity
# - pressure drop:
#   - ideal: NOT IMPLEMENTED
#   - base: tube section from base
#   plus : maximum pressure drop

sizing_method = ['velocity', 'base', 0.5]
# sizing_method = ['pressure_drop', 'base', 50.]
choice = 1  # choice of test (0-3)
random_length = False
pump_model = False
material = 0  # material can be 0=iron, 1=copper or 2=pehd (the material can be changed from section to section)
nominal_flowrate = 2.5/3.6  # nominal pump flow rate in kg/s
# plot = ['velocity', 'flowrate', 'diameter']  # plots graph layout with values velocity, flowrate and diameter
plot = ['flowrate','length']  # plots graph layout with values velocity, flowrate and diameter
singular_share = 0.5  # share of pressure drop due to singular flow resistances
launch(choice=choice, material=material, singular_share=singular_share, random_length=random_length, nominal_flowrate=nominal_flowrate,
       plot=plot, sizing_method=sizing_method, sizing_tubes=True, pump_model=pump_model, plot_pump_curves=True)
