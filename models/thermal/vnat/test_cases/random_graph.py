import matplotlib.pyplot as plt
import numpy as np
import networkx as nx


def random_network(n_size, rho_ref, toplot=False):

    G = nx.complete_graph(n_size)
    if toplot:
        nx.draw_networkx(G, with_labels=True)
        plt.show()

    t_ext = 15.

    nodes = {}
    for node in G.nodes:
        if np.mod(node, 3) == 0:
            ext_pressure = float(np.random.random(1)*100.)
            nodes['N' + str(node)] = {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': ext_pressure, 'x': -1, 'y': 0, 'z': 0}
        else:
            nodes['N' + str(node)] = {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 0}

    path_list = []
    flow_paths = {}
    counter = 0
    for node_1 in nodes:
        for node_2 in nodes:
            if [nodes[node_1]['type'], nodes[node_2]['type']] != ['boundary_condition', 'boundary_condition']:
                if ([node_2, node_1] not in path_list) and (node_2 != node_1):  # external to internal node connection
                    if [nodes[node_1]['type'], nodes[node_2]['type']] == ['node', 'node']:  # internal connection via "door"
                        choice = np.round(np.random.random(1)*2, 0)
                        if choice == 0:  # door
                            flow_paths['B' + str(counter)] = {'path': [node_1, node_2], 'z': 0,
                                                              'connection': {'connection_type': 'door', 'section': 2.0, 'discharge_coefficient': 0.6, 'n': 0.5}}
                        elif choice == 1:  # duct dtu
                            flow_paths['B' + str(counter)] = {'path': [node_1, node_2], 'z': 0,
                                                              'connection': {'connection_type': 'duct_dtu', 'h_diam': 0.08, 'section': 0.005, 'length': 2, 'coefK': 9.e6, 'dzeta': [0.6, 0.6]}}

                    else:
                        if ([node_2, node_1] not in path_list) and (node_2 != node_1):  # external to internal node connection
                            choice = np.round(np.random.random(1)*2, 0)
                            if choice == 0:
                                flow_paths['B' + str(counter)] = {'path': [node_1, node_2], 'z': 0,
                                                                  'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30, 'n': 0.5}}
                            elif choice == 1:
                                flow_paths['B' + str(counter)] = {'path': [node_1, node_2], 'z': 0,
                                                                  'connection': {'connection_type': 'outlet_grille', 'dp0': 80, 'rho0': rho_ref, 'flow0': 45, 'n': 0.5}}

                        counter += 1
                        path_list.append([node_1, node_2])

    return flow_paths, nodes

