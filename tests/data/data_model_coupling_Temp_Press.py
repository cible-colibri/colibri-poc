from core.constants import rho_ref

flow_paths = {'B0': {'path': ['BC0', 'living_room_1'], 'z': 0,
                     'connection': {'connection_type': 'inlet_grille', 'dp0': 20, 'rho0': rho_ref, 'flow0': 30,
                                    'n': 0.5}},
              'B1': {'path': ['living_room_1', 'kitchen_1'], 'z': 0,
                     'connection': {'connection_type': 'door', 'section': 0.008, 'discharge_coefficient': 0.6,
                                    'n': 0.5}},
              'B2': {'path': ['kitchen_1', 'BC1'], 'z': 0,
                     'connection': {'connection_type': 'outlet_grille', 'dp0': 80, 'rho0': rho_ref, 'flow0': 45,
                                    'n': 0.5}}}

nodes = {'living_room_1': {'type': 'node', 'temperature': 20, 'volume': 52.25, 'x': 0, 'y': 0, 'z': 0},
         'kitchen_1': {'type': 'node', 'temperature': 20, 'volume': 23.8, 'x': 1, 'y': 1, 'z': 0},
         'BC0': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': -1, 'y': 0, 'z': 0},
         'BC1': {'type': 'boundary_condition', 'temperature': 20, 'pressure': 0, 'x': 3, 'y': 0, 'z': 0}
         }