import numpy as np


def boundary_matrix(weather, nodes, t_final, dynamic_test, apply_disturbance):

    t = np.arange(t_final)

    node_nb = 0
    for node in nodes:
        if nodes[node]['type'] == 'boundary_condition':
            node_nb += 1
            pressure = - 80. + dynamic_test * (np.cos(t * np.pi / 120 * node_nb)) * 50.
            # pressure = - 80. + node_nb * 150. + np.zeros(len(t))
            if apply_disturbance[1] > 0:
                pressure[(np.mod(t, apply_disturbance[1]) == 0) & (t != 0)] += apply_disturbance[0] * node_nb
            nodes[node]['pressure_list'] = pressure
            nodes[node]['temperature_list'] = weather.ext_temperature
