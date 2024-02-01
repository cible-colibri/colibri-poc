import matplotlib.pyplot as plt
import numpy as np
from models.thermal.vnat.test_cases.data_model import flow_paths, nodes
import networkx as nx


def construct_connectivity_matrix(flow_paths, nodes):
    node_names = list(nodes.keys())
    N = len(node_names)
    matrix = np.zeros((N,N))

    for flow_path in flow_paths.values():
        i = node_names.index(flow_path['path'][0])
        j = node_names.index(flow_path['path'][1])
        matrix[i,j] = 1
        matrix[j,i] = 1

    return matrix


def import_into_networkx(flow_paths, nodes):
    G = nx.Graph()

    for node_name, node_attrs in nodes.items():
        G.add_node(node_name, attr_dict=node_attrs)

    for flow_path in flow_paths.values():
        G.add_edge(flow_path['path'][0], flow_path['path'][1], attr_dict=flow_path['connection'])

    return G


def plot_test_case():
    fig = plt.figure()
    # plot nodes
    for n in nodes:
        if nodes[n]['type'] == 'node':
            plt.plot(nodes[n]['x'], nodes[n]['y'], 'ko')
            plt.text(nodes[n]['x'], nodes[n]['y'] + 0.1, '? Pa')
        else:  # boundary
            plt.plot(nodes[n]['x'], nodes[n]['y'], 'rs')
            plt.text(nodes[n]['x'], nodes[n]['y'] + 0.1, str(nodes[n]['pressure'])+' Pa')

    # plot flow paths
    for p in flow_paths:
        from_node = flow_paths[p]['path'][0]
        to_node = flow_paths[p]['path'][1]
        plt.plot([nodes[from_node]['x'], nodes[to_node]['x']], [nodes[from_node]['y'], nodes[to_node]['y']])
        plt.text((nodes[from_node]['x'] + nodes[to_node]['x'])/2, (nodes[from_node]['y'] + nodes[to_node]['y'])/2, p)

    plt.axis('Off')
    plt.show()
    return fig


# fig = plot_test_case()
#connectivity_matrix = construct_connectivity_matrix(flow_paths, nodes)
#print(connectivity_matrix)
# G = import_into_networkx(flow_paths, nodes)
# pos = nx.spring_layout(G)
# nx.draw(G,labels={node: node for node in G.nodes()})
# nx.draw_networkx_edge_labels(G, pos, edge_labels={edge: edge for edge in G.edges()})
# plt.show()