import json
import os
import numpy as np
from models.thermal.vnat.test_cases.random_graph import random_network

rho_ref = 1.204785775
t_ref = 20.
t_ref_K = 273.15
t_ext = -20
g = 9.81
p_ref = 101300
Rs_air = 287
cp_air_ref = 1006.

main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

def set_test(model, apply_buoyancy):
    if model == 1:
        flow_paths = {'B0': {'path': ['BC0', 'N0'], 'z': 0,
                             'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30, 'n': 0.5}},
                      'B1': {'path': ['N0', 'N1'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B2': {'path': ['N1', 'N3'], 'z': 5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B3': {'path': ['N0', 'N2'], 'z': 7.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B4': {'path': ['N2', 'N3'], 'z': 10,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B5': {'path': ['N3', 'BC1'], 'z': 0,
                             'connection': {'connection_type': 'vent_volume_flow', 'flow_rate': 20}},
                      }

        nodes = {'N0': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 2},
                 'N1': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': 1, 'z': 4},
                 'N2': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': -1, 'z': 6},
                 'N3': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 2, 'y': 0, 'z': 8},
                 'BC0': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': 0, 'x': -1, 'y': 0, 'z': 10},
                 'BC1': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': -80, 'x': 3, 'y': 0, 'z': 12.5}
                 }

    elif model == 2:

        flow_paths = {'B0': {'path': ['BC0', 'N0'], 'z': 0,
                             'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30,
                                            'n': 0.5}},
                      'B1': {'path': ['N0', 'N1'], 'z': 0,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6,
                                            'n': 0.5}},
                      'B2': {'path': ['N1', 'BC1'], 'z': 0,
                             'connection': {'connection_type': 'outlet_grille', 'dp0': 80, 'rho0': rho_ref, 'flow0': 45,
                                            'n': 0.5}}}

        nodes = {'N0': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 0},
                 'N1': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': 1, 'z': 0},
                 'BC0': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': -1, 'y': 0, 'z': 0},
                 'BC1': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': 3, 'y': 0, 'z': 0}
                 }

    elif model == 3:
        flow_paths = {'B0': {'path': ['BC0', 'N0'], 'z': 0,
                             'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30, 'n': 0.5}},
                      'B1': {'path': ['N0', 'N1'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B2': {'path': ['N0', 'N2'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B3': {'path': ['N1', 'N3'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B4': {'path': ['N2', 'N3'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B5': {'path': ['N3', 'BC1'], 'z': 0,
                             'connection': {'connection_type': 'fan_mechanical', 'pressure_curve': [[0, 30, 100, 1000], [150, 120, 100, 50]]}},
                      }

        nodes = {'N0': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 2},
                 'N1': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 2, 'y': 0, 'z': 8},
                 'N2': {'type': 'node', 'temperature': 20, 'volume': 0, 'x': 2, 'y': 0, 'z': 8},
                 'N3': {'type': 'node', 'temperature': 20, 'volume': 0, 'x': 2, 'y': 0, 'z': 8},
                 'BC0': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': 0, 'x': -1, 'y': 0, 'z': 10},
                 'BC1': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': 0, 'x': 3, 'y': 0, 'z': 12.5}
                 }

    elif model == 4:
        flow_paths = {'B0': {'path': ['BC0', 'N0'], 'z': 0,
                             'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30, 'n': 0.5}},
                      'B1': {'path': ['N0', 'N1'], 'z': 2.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B2': {'path': ['N1', 'N3'], 'z': 5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B3': {'path': ['N0', 'N2'], 'z': 7.5,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B4': {'path': ['N2', 'N3'], 'z': 10,
                             'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6, 'n': 0.5}},
                      'B5': {'path': ['N3', 'N4'], 'z': 12.5,
                             'connection': {'connection_type': 'outlet_grille', 'dp0': 80, 'rho0': rho_ref, 'flow0': 45, 'n': 0.5}},
                      'B6': {'path': ['N4', 'N5'], 'z': 0,
                             'connection': {'connection_type': 'duct_dtu', 'h_diam': 0.080, 'section': 0.005, 'length': 5, 'coefK': 3.e6, 'dzeta': [0.0006, 0.0006]}},
                      'B7': {'path': ['N5', 'BC1'], 'z': 0,
                             'connection': {'connection_type': 'fan_mechanical',
                                            'pressure_curve': [[0, 30, 100, 10000], [150, 120, 100, 50]]}},
                      }

        nodes = {'N0': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 2},
                 'N1': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': 1, 'z': 4},
                 'N2': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': -1, 'z': 6},
                 'N3': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 2, 'y': 0, 'z': 8},
                 'N4': {'type': 'node', 'temperature': 20, 'volume': 0, 'x': 2, 'y': 0, 'z': 8},
                 'N5': {'type': 'node', 'temperature': 20, 'volume': 0, 'x': 2, 'y': 0, 'z': 8},
                 'BC0': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': 0, 'x': -1, 'y': 0, 'z': 10},
                 'BC1': {'type': 'boundary_condition', 'temperature': t_ext, 'pressure': 0, 'x': 3, 'y': 0, 'z': 12.5}
                 }

    elif model == 5:

        flow_paths = {'B0': {'path': ['BC0', 'N0'], 'z': 0,
                             'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30, 'n': 0.5}},
                      'B1': {'path': ['N0', 'N1'], 'z': 0,
                             'connection': {'connection_type': 'duct_dtu', 'h_diam': 0.08, 'section': 0.005, 'length': 5, 'coefK': 3.e6, 'dzeta': [0.6, 0.6]}},
                      'B2': {'path': ['N1', 'BC1'], 'z': 0,
                             'connection': {'connection_type': 'outlet_grille', 'dp0': 80, 'rho0': rho_ref, 'flow0': 45,'n': 0.5}}
                      }

        nodes = {'N0': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 0, 'y': 0, 'z': 0},
                 'N1': {'type': 'node', 'temperature': 20, 'volume': 50, 'x': 1, 'y': 1, 'z': 0},
                 'BC0': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': -1, 'y': 0, 'z': 0},
                 'BC1': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': 3, 'y': 0, 'z': 0}
                 }

    elif 'load_' in model:
        n_size = model[5::]
        f = open(main_dir + '/test_cases/dict_' + n_size + '.json')
        dict_case = json.load(f)
        nodes = dict_case['nodes']
        flow_paths = dict_case['flow_paths']

    elif isinstance(model, str):
        n_size = int(model)
        flow_paths, nodes = random_network(n_size, rho_ref, toplot=True)
        dict_case = {}
        dict_case['nodes'] = nodes
        dict_case['flow_paths'] = flow_paths
        with open(main_dir + '/test_cases/dict_' + str(n_size) + '.json', 'w') as fp:
            json.dump(dict_case, fp, indent=4)

    if apply_buoyancy:
        for node in nodes:
            if nodes[node]['type'] == 'node':
                nodes[node]['temperature'] = 20. + np.random.random() * 5.
            else:
                nodes[node]['temperature'] = -20. + np.random.random() * 50.
            nodes[node]['z'] = np.random.random() * 10.

        for flow_path in flow_paths:
            flow_paths[flow_path]['z'] = np.random.random() * 10.


    return flow_paths, nodes