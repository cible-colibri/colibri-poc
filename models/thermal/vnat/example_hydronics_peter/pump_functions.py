import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.interpolate import interp1d


def pump_chars(flowrate_nominal=1., check_curve=False):
    # generate pump curve as table
    data_matrix = np.array([[0., 6.],[2., 4.],[4., 2.75],[6., 1.7], [8.,0.75],[10.,0.4],[11.,0.]])  # table with ((flow_1, dp_1), ... (flow_n, dp_n))
    x_coeff = 1./60.*flowrate_nominal  # scale for flow rate kg/s
    y_coeff = 1e4  # scale for pump head Pa
    #TODO: dans sizer
    data_matrix[:, 0] *= x_coeff  # convert to kg/s
    data_matrix[:, 1] *= y_coeff  # convert to Pa

    # maximum flowrate of pump
    flowrate_max = np.max(data_matrix[:,0])
    n_discret = 100  # generate n points

    # ############# first method #############
    #
    # pump_data_table = np.zeros((n_discret+1,2))  # create empty table
    # flow_table = np.array(range(n_discret+1)) / n_discret * flowrate_max  # generate flow rates in new table
    # dp_pump_table = np.zeros(len(flow_table))  # initialise corresponding pump heads
    # for i, flow in enumerate(flow_table):
    #     dp_pump_table[i] = interpolate_linear(flow, data_matrix)  # fill in pump heads
    # pump_data_table[:, 0] = flow_table  # fill in in pump_data_table which is used in the pump model
    # pump_data_table[:, 1] = dp_pump_table  # fill in in pump_data_table which is used in the pump model

    ############## method with scipy ###############

    pump_data_table = np.zeros((n_discret+1, 2))  # create empty table
    pump_data_table[:, 0] = np.array(range(n_discret+1)) / n_discret * flowrate_max  # generate flow rates in new table
    f = interp1d(data_matrix[:, 0], data_matrix[:, 1])  # Can use quadratic interpolation with kind='quadratic'
    pump_data_table[:, 1] = f(pump_data_table[:, 0])
    # TODO: vérifier dernière valeur --> ValueError when the value is over the interpolation range. I let you decide what you prefer to do: better raise the error or put a limitation ?

    if check_curve:  # plot curve for visual checking
        plt.plot(data_matrix[:, 0], data_matrix[:, 1], 'k+', label='Pump States', markersize=20)
        plt.plot(pump_data_table[:, 0], pump_data_table[:, 1], 'go', markersize=3, label='Linear Interpolation scipy')
        plt.xlabel('Flow rate [l/min]')
        plt.ylabel('Pump head [Pa]')
        plt.title('Pump curve verification')
        plt.legend()
        plt.show()

    return pump_data_table


def interpolate_linear(state_act, data_matrix):
    # function for linear interpolation
    # example: data_matrix = np.array([[35., 0.85],[55., 0.77],[75., 0.73]], dtype=np.float32)
    states = data_matrix[:, 0]
    results = data_matrix[:, 1]

    if state_act <= states[0]:
        result_act = results[0]
    elif state_act >= states[-1]:
        result_act = results[-1]
    else:

        for i in range(len(states) - 1):
            if (state_act > states[i]) and (state_act <= states[i + 1]):
                state_diff = states[i+1]-states[i]
                if state_diff == 0.:
                    result_act = 0.
                    raise ValueError('Wrong matrix')
                else:
                    alpha = (results[i+1]-results[i])/state_diff
                    q = results[i+1] - alpha * states[i+1]
                    result_act = alpha * state_act + q

    return result_act


def pump(flowrate, pressure_drop, pump_speed, pump_data_table, pump_speed_nominal, toplot, niter, fig, ax, pump_efficiency=0.25):
    """
    Pump model

    :param flowrate: previous flowrate of the pump
    :param pressure_drop: pressure drop calculate from the balance
    :param pump_speed: given pump speed
    :param pump_data_table: characteristics of the pump based on the nominal flowrate
    :param pump_speed_nominal:
    :param toplot:
    :param niter:
    :param fig:
    :param ax:
    :param pump_efficiency:
    :return:
    """

    # load pump table
    pump_flow_table = pump_data_table[:, 0]
    dp_pump_table = pump_data_table[:, 1]

    # calculate flow-dp for grid from Cnetwork based on last time step
    Cnetwork = pressure_drop / flowrate**2  # coefficient with data of last time step
    dp_grid_table = Cnetwork * pump_flow_table**2

    # find closest result for pump-grid crossing
    teou = np.argwhere(np.abs(dp_grid_table-dp_pump_table) == np.min(np.abs((dp_grid_table-dp_pump_table))))
    flowrate = float(pump_flow_table[teou])  # get flow rate that corresponds

    # set outlet pressure to 0
    outlet_pressure = 0.  # pressure_drop*0.
    pump_power = 9.81 * pressure_drop / 1e4 * flowrate / pump_efficiency  # pump efficiency is pump and motor efficiency product - typical values between 10 - 60 %

    if toplot:
        if np.mod(niter,100) == 1:
            ax.clear()
            line1, = ax.plot(pump_flow_table, dp_pump_table)
            line2, = ax.plot(pump_flow_table, dp_grid_table)
            ax.set_ylim(0., 1e5)
            fig.canvas.draw()

    return flowrate, pump_power, fig, ax
