import numpy as np
from numpy import eye
from scipy.linalg import expm, inv
epsilon = 1e-15
from models.thermal.vnat.test_cases.data_model import rho_ref, cp_air_ref


def set_U_from_index(U, index_inputs, label, value_to_set, add=False):
    if add:
        U[index_inputs[label]['start_index']:index_inputs[label]['start_index'] + index_inputs[label]['n_elements']] += value_to_set
    else:
        U[index_inputs[label]['start_index']:index_inputs[label]['start_index'] + index_inputs[label]['n_elements']] = value_to_set


def get_states_from_index(states, index_states, label):
    return states[index_states[label]['start_index']:index_states[label]['start_index'] + index_states[label]['n_elements']]


def runStateSpace(Ad, Bd, X, U):
    return np.dot(Ad, X) + np.dot(Bd, U)


def generate_euler_exp_Ad_Bd(A,B,dt, label='None'):
    n_total_nodes = np.shape(A)[0]
    try:
        Ad = expm(A * dt)
    except Exception:
        raise ValueError('Object {name} exponential A matrix cannot be computed'.format(name=label))

    try:
        Bd = inv(A).dot(Ad - eye(n_total_nodes)).dot(B)
    except Exception:
        raise ValueError('Object {name} exponential A matrix is singular'.format(name=label))

    Ad[np.where(Ad < epsilon)] = 0
    Bd[np.where(Bd < epsilon)] = 0

    return Ad, Bd


def get_rad_shares(Boundary_list, Window_list, Space_list):

    for space in Space_list:  # go through all spaces
        space.envelope_area = 0.
        space.envelope_list = {}
        for obj in Boundary_list:  # look which boundary is in contact with the current space
            if ('floor' in obj.label) or ('plancher' in obj.label):  # TODO; c'est pas beau et peut planter si on ne nomme pas pareil
                env_type = 'floor'
            else:
                env_type = 'other'
            # if it is an internal wall in a space, both sides are accounted for (very simplified)
            if obj.side_1 == space.label:  # this side is in contact with the current space
                if env_type != 'floor':
                    space.envelope_area += obj.area
                if obj.side_2 == 'exterior':
                    u_value = obj.u_value
                else:
                    u_value = 0.
                space.envelope_list[obj.label] = {'type': env_type, 'area': obj.area, 'side': 'side_1', 'u_value': u_value}
            if obj.side_2 == space.label:  # this side is in contact with the current space
                if env_type != 'floor':
                    space.envelope_area += obj.area
                if obj.side_1 == 'exterior':
                    u_value = obj.u_value
                else:
                    u_value = 0.
                space.envelope_list[obj.label] = {'type': env_type, 'area': obj.area, 'side': 'side_2', 'u_value': u_value}
        for obj in Window_list:  # look which boundary is in contact with the current space
            # if it is an internal wall in a space, both sides are accounted for (very simplified)
            if obj.side_1 == space.label:  # this side is in contact with the current space
                space.envelope_area += obj.area
                space.envelope_list[obj.label] = {'type': 'window', 'area': obj.area, 'side': 'side_1',
                                                  'boundary_name': obj.bound_name, 'transmittance': obj.transmittance,
                                                  'u_value': obj.u_value}
            if obj.side_2 == space.label:  # this side is in contact with the current space
                space.envelope_area += obj.area
                space.envelope_list[obj.label] = {'type': 'window', 'area': obj.area, 'side': 'side_1',
                                                  'boundary_name': obj.bound_name, 'transmittance': obj.transmittance,
                                                  'u_value': obj.u_value}

    # no go through again and associate radiative distribution shares
    floor_rad_share = 0.642  # bestest value ...

    for space in Space_list:
        for env in space.envelope_list:
            if space.envelope_list[env]['type'] == 'floor':
                rad_share = floor_rad_share
            else:
                rad_share = space.envelope_list[env]['area'] / space.envelope_area * (1-floor_rad_share)
            space.envelope_list[env]['radiative_share'] = rad_share
    # check if sum is 1
    for space in Space_list:
        checker = 0.
        for env in space.envelope_list:
            checker += space.envelope_list[env]['radiative_share']
        if np.abs(checker - 1) > 1e-5:
            raise ValueError('radiative share calculation is wrong. The sum of all shares should be equal to 1, but is ', checker)


def get_u_values(Space_list):
    u_wall = 0.
    wall_area = 0.
    u_window = 0.
    window_area = 0.
    for obj in Space_list:
        for env in obj.envelope_list:
            element = obj.envelope_list[env]
            if element['type'] != 'window':
                u_wall += element['u_value'] * element['area']
                wall_area += element['area']
            else:
                u_window += element['u_value'] * element['area']
                window_area += element['area']
        u_wall /= wall_area
        u_window /= window_area
        obj.u_wall = u_wall
        obj.u_window = u_window
        obj.wall_area = wall_area
        obj.window_area = window_area


def gen_wall_model(boundary):
    # generates the resistances between all nodes in all layers of a boundary (wall, ceiling, floor)
    # input is either a class instance or a Namedtuple "boundary"

    # load properties
    thickness = boundary.thickness
    cond      = boundary.thermal_conductivity
    rho       = boundary.density
    cp        = boundary.specific_heat
    discret   = boundary.discret  # number of layer discretisation

    N = sum(discret) + 2  # total number of nodes (N nodes plus 2 surface nodes
    x = np.zeros(N)  # x position of nodes starting from side_1 = 0. Side_2 = total thickness
    resistance = np.zeros(N-1)  # thermal resistance of node
    mcp = np.zeros(N)  # thermal mass of node
    j = 0  # counter of nodes

    # first surface node at side_1
    x[j] = 0.
    mcp[j] = thickness[0] / (discret[0] + 1) / 100. * rho[0] * cp[0]  # very thin cover layer at surface, no mass
    j += 1

    # intermediate nodes that are not at the surface
    for lay in range(len(thickness)):  # go through each layer
        for i in range(discret[lay]):
            if (lay > 0) and (i == 0):  # internal interface between 2 different layers
                x[j]            = x[j-1] + thickness[lay-1] / (discret[lay-1] + 1) + thickness[lay] / (discret[lay] + 1)
                resistance[j-1] = thickness[lay-1] / (discret[lay-1] + 1) / cond[lay-1] + thickness[lay] / (discret[lay] + 1) / cond[lay]
                mcp[j]          = thickness[lay-1] / (discret[lay-1] + 1) * rho[lay-1] * cp[lay-1] + thickness[lay] / (discret[lay] + 1) * rho[lay] * cp[lay]
            else:  # all other nodes
                x[j]            = x[j-1] + thickness[lay]/(discret[lay] + 1)
                resistance[j-1] = thickness[lay] / (discret[lay] + 1) / cond[lay]
                mcp[j]          = thickness[lay] / (discret[lay] + 1) * rho[lay] * cp[lay]
            j += 1

    # last node towards side_2
    x[j] = sum(thickness)
    resistance[j-1] = thickness[lay] / (discret[lay] + 1) / cond[lay]
    mcp[j] = thickness[lay] / (discret[lay] + 1) / 100. * rho[lay] * cp[lay]

    # calculate distance between nodes
    # dx = np.diff(x)
    boundary.resistance = resistance
    boundary.u_value = 1/np.sum(resistance)
    boundary.thermalmass = mcp * boundary.area
    return boundary


def create_idict(Boundary_list, Window_list, Space_list):
    i_dict = {}
    i = 0
    for obj in Boundary_list:
        nnodes = len(obj.thermalmass)
        for node in range(nnodes):
            i_dict[obj.label + '__node_nb_' + str(node)] = i
            i += 1

    for obj in Window_list:
        i_dict[obj.label + '__ext'] = i
        i += 1
        i_dict[obj.label + '__int'] = i
        i += 1

    for obj in Space_list:  # mean radiant nodes
        i_dict[obj.label + '__mr'] = i
        i += 1

    for obj in Space_list:  # air nodes
        i_dict[obj.label + '__air'] = i
        i += 1

    return i_dict


def estimate_hrad(emissivity, temperature_surface, temperature_client):
    # estimate linear radiant heat transfer coefficient
    temperature_surface += 273.15
    temperature_client += 273.15
    if temperature_surface == temperature_client:
        temperature_client += 1e-3
    h_rad = 5.667e-8 * emissivity * (temperature_surface ** 4 - temperature_client ** 4) / (temperature_surface - temperature_client)
    return h_rad


def estimate_hconv(obj_type, tilt, ext=False, mode='heating'):
    # standard convective heat exchange coefficients in W/m2/K
    # tilt = 0   : floor is side_1, ceiling side_2
    # tilt = 180 : floor is side_2, ceiling side_1
    h_dict = {'0':   {'heating': 2., 'cooling': 1., 'freefloat': 1.5},
              '180': {'heating': 1., 'cooling': 2., 'freefloat': 1.5},
              '90':  {'heating': 3., 'cooling': 3., 'freefloat': 3.}}
    if (tilt != 0) & (tilt != 180):
        tilt = 90
    if ext:
        if obj_type == 'window':
            h_conv = 15.
        else:
            h_conv = 15.
    else:  # interior
        if obj_type == 'window':
            h_conv = 3.
        else:  # opac
            h_conv = h_dict[str(tilt)][mode]
    return h_conv

def estimate_hconv_(obj_type, tilt, ext=False, mode='heating'):
    # standard convective heat exchange coefficients in W/m2/K
    # tilt = 0   : floor is side_1, ceiling side_2
    # tilt = 180 : floor is side_2, ceiling side_1
    h_dict = {'0':   {'heating': 9.26-5.13, 'cooling': 2.2, 'freefloat': 2.2},
              '180': {'heating': 6.13-5.13, 'cooling': 1.8, 'freefloat': 1.8},
              '90':  {'heating': 8.29-5.13, 'cooling': 3.5, 'freefloat': 3.5}}
    if (tilt != 0) & (tilt != 180):
        tilt = 90
    if ext:
        if obj_type == 'window':
            h_conv = 24.3
        else:
            h_conv = 24.3
    else:
        if obj_type == 'window':
            h_conv = 3.29
        else:
            h_conv = 3.29#h_dict[str(tilt)][mode]
    return h_conv


def u_value_window(r_window, h_rad_ext, h_rad_int, h_conv_ext=8.0, h_conv_int=2.4):
    # window parameters (using same hrad and hconv coefficients as walls)
    # estimate instrincis U value of envelope element. Instrinsic means from one surface node to the other one.
    try:
        r_window_int = r_window - 1. / (h_conv_ext + h_rad_ext) - 1. / (h_conv_int + h_rad_int)
        windows_u_value_intr = 1. / r_window_int
    except IndexError:
        windows_u_value_intr = 0.
    if windows_u_value_intr <= 0:  # in case that U-values has been set to high, not coherent with heat exchange coefficients
        windows_u_value_intr = 0.01
    return windows_u_value_intr


def generate_A_and_B(Space_list, Boundary_list, Window_list):

    # n_total_nodes = sum(space_air, space_tmr, windows * 2 nodes, boundaries * sum(layer_i * discret_i)
    n_spaces = len(Space_list)
    n_windows = len(Window_list)
    n_boundaries = len(Boundary_list)
    n_wall_layers = 0

    for bound in Boundary_list:
        n_wall_layers += len(bound.thermalmass)
    n_total_nodes = n_spaces * 2 + n_windows * 2 + n_wall_layers
    index_states = {'boundaries': {'start_index': 0, 'n_elements': n_wall_layers},
                    'windows': {'start_index': n_wall_layers, 'n_elements': 2 * n_windows},
                    'spaces_mean_radiant': {'start_index': n_wall_layers + 2 * n_windows, 'n_elements': n_spaces},
                    'spaces_air': {'start_index': n_wall_layers + 2 * n_windows + n_spaces, 'n_elements': n_spaces}
                    }

    # n_inputs for U array =
    #   - external boundaries and integrated windows
    #       - Tground (scalar)
    #       - Tair_ext (for each boundary)
    #       - Tmr_ext (for each boundary)
    #       - phi_radiative_external (for each boundary)
    #   - internal air spaces
    #       - phi_radiative_internal (for each space)
    #       - space_convective_gain (for each space)


    index_inputs = {'ground_temperature': {'start_index': 0, 'n_elements': 1},
                    'exterior_air_temperature': {'start_index': 1, 'n_elements': n_boundaries},
                    'exterior_radiant_temperature': {'start_index': 1 * n_boundaries + 1, 'n_elements': n_boundaries},
                    'radiative_gain_boundary_external': {'start_index': 2 * n_boundaries + 1, 'n_elements': n_boundaries},
                    'space_radiative_gain': {'start_index': 3 * n_boundaries + 1, 'n_elements': n_spaces},
                    'space_convective_gain': {'start_index': 3 * n_boundaries + 1 + n_spaces, 'n_elements': n_spaces},
                    }

    n_inputs = 1 + 4 * n_boundaries + n_spaces

    # Initialise A and B matrices
    A = np.zeros((n_total_nodes, n_total_nodes))
    B = np.zeros((n_total_nodes, n_inputs))
    mcp = np.zeros(n_total_nodes)

    # create a dict with the indexes of rows related to ID's
    i_dict = create_idict(Boundary_list, Window_list, Space_list)

    # now fill in A and B with known indexes
    # i0_boundaries = 0
    flux_B_indexing = []
    bound_nb = 0
    i = 0
    for obj in Boundary_list:
        nnodes = len(obj.thermalmass)
        for node in range(nnodes):
            if (node == 0) or (node == nnodes-1):  # side 1 and side 2
                if node == 0:
                    side = obj.side_1
                elif node == nnodes-1:
                    side = obj.side_2
                else:
                    pass
                if side == "exterior":  # to ext, so fill in negative on diag(A) and positive in B
                    # surface exchange with external air node, fill in B only
                    # convective coefficients
                    h_conv = estimate_hconv('opaque', obj.tilt, ext=True)
                    print('Boundary: ', obj.label, 'surface : ', side, 'hconv : ', h_conv)
                    i_to_air = index_inputs['exterior_air_temperature']['start_index'] + bound_nb  # index for air temperature of each boundary is equal to the number of boundary
                    B[i, i_to_air] += h_conv * obj.area
                    # long wave radiation coefficients
                    h_rad = estimate_hrad(obj.emissivity[0], 10.0, 0.0)  # radiant coefficient at external surface towards outside
                    print('Boundary: ', obj.label, 'surface : ', side, 'hrad : ', h_rad)
                    i_to_mr = index_inputs['exterior_radiant_temperature']['start_index'] + bound_nb  # index for mean radiant external temperature of each boundary is equal to the number of boundary
                    B[i, i_to_mr] += h_rad * obj.area
                    # flux indexing ans scaling (applied at the end of this function, to allow calculation of diagonal of A)
                    # radiative flux is in W/m², i.e. coefficient is the area of the element
                    flux_B_indexing.append([i, index_inputs['radiative_gain_boundary_external']['start_index'] + bound_nb, obj.area])  # radiative_gain_boundary_external

                elif side == 'ground':  # fill in B only
                    resistance_ground_1m = 1.0 / 2.0  # 1m distance and conductivity of 2.0 W/m/K, could be made for specific ground
                    i_ground = index_inputs['ground_temperature']['start_index']
                    B[i, i_ground] += 1/resistance_ground_1m * obj.area

                elif side == 'boundary':  # fill in B only
                    # remark: in case of specification of "boundary", the field "exterior_air_temperature" is used, and "exterior_radiant_temperature" not connected
                    resistance_boundary = 1e-10  # very small resistance to connect directly the boundary temperature
                    i_boundary = index_inputs['exterior_air_temperature']['start_index'] + bound_nb
                    B[i, i_boundary] += 1/resistance_boundary * obj.area

                else:  # internal air space, fill inside A only
                    # search corresponding air node index
                    h_conv = estimate_hconv('opaque', obj.tilt)
                    print('Boundary: ', obj.label, 'surface : ', side, 'hconv : ', h_conv)
                    i_to_air_node = list(i_dict).index(side+'__air')
                    A[i, i_to_air_node] += h_conv * obj.area
                    A[i_to_air_node, i] += h_conv * obj.area

                    # search corresponding air node index
                    h_rad = estimate_hrad(obj.emissivity[0], 20.0, 20.0)
                    print('Boundary: ', obj.label, 'surface : ', side, 'hrad : ', h_rad)
                    i_to_mr_node = list(i_dict).index(side + '__mr')
                    A[i, i_to_mr_node] += h_rad * obj.area
                    A[i_to_mr_node, i] += h_rad * obj.area

                    # flux indexing (applied at the end of this function, to allow calculation of diagonal of A)
                    space_count = 0
                    for space in Space_list:
                        for env in space.envelope_list:
                            if env == obj.label:  # we found it
                                radiative_share = space.envelope_list[env]['radiative_share']
                                flux_B_indexing.append([i, index_inputs['space_radiative_gain']['start_index'] + space_count, radiative_share])  # radiative_gain_boundary_external
                        space_count += 1

                # conduction towards next (node = 0) or previous node (node == nnodes)
                if node == 0:
                    A[i, i+1] += 1 / obj.resistance[node] * obj.area
                elif node == nnodes-1:
                    A[i, i-1] += 1 / obj.resistance[node-1] * obj.area
                else:
                    pass

            else:  # internal material nodes, only conduction
                A[i, i+1] = 1 / obj.resistance[node] * obj.area
                A[i, i-1] = 1 / obj.resistance[node-1] * obj.area
            mcp[i] = obj.thermalmass[node]
            i += 1

        bound_nb += 1

    # now i is the first index of windows
    for obj in Window_list:
        for node in range(2):  # window in this model has 2 nodes: internal surface node and external surface node
            if node == 0:  # side 1
                side = obj.side_1
            else:  # side 2
                side = obj.side_2

            if side == "exterior":  # to ext, so fill in B
                # surface exchange with external air node, fill in B only
                # convective coefficients
                h_conv = estimate_hconv('window', obj.tilt, ext=True)  # perhaps values for single 6, double 4.5 and triple glazing? 3
                print('Boundary: ', obj.label, 'surface : ', side, 'hconv : ', h_conv)
                i_to_air = index_inputs['exterior_air_temperature']['start_index'] + obj.bound_nb  # index for air temperature of each boundary is equal to the number of boundary
                B[i, i_to_air] += h_conv * obj.area
                # long wave radiation coefficients
                h_rad  = estimate_hrad(obj.emissivity[0], 10.0, 0.0)  # radiant coefficient at external surface towards outside
                print('Boundary: ', obj.label, 'surface : ', side, 'hrad : ', h_rad)
                i_to_mr = index_inputs['exterior_radiant_temperature']['start_index'] + obj.bound_nb  # index for mean radiant external temperature of each boundary is equal to the number of boundary
                B[i, i_to_mr] += h_rad * obj.area
                # flux indexing (applied at the end of this function, to allow calculation of diagonal of A)
                # radiative flux is in W/m², i.e. coefficient is the area of the element
                flux_B_indexing.append([i, index_inputs['radiative_gain_boundary_external']['start_index'] + obj.bound_nb, obj.area * obj.absorption])  # radiative_gain_boundary_external absorbed by window
                # TODO: solar transmission into zone

            else:  # internal air space, fill inside A only
                # search corresponding air node index
                # convective heat exchange coefficients
                h_conv = estimate_hconv('window', obj.tilt)  # Todo: window h_conv depends on glazing type and temperature difference, different to walls
                print('Boundary: ', obj.label, 'surface : ', side, 'hconv : ', h_conv)
                i_to_air_node = list(i_dict).index(side+'__air')
                A[i, i_to_air_node] += h_conv * obj.area
                A[i_to_air_node, i] += h_conv * obj.area
                # long wave radiation coefficients
                h_rad = estimate_hrad(obj.emissivity[1], 20.0, 20.0)
                print('Boundary: ', obj.label, 'surface : ', side, 'hrad : ', h_rad)
                i_to_mr_node = list(i_dict).index(side + '__mr')
                A[i, i_to_mr_node] += h_rad * obj.area
                A[i_to_mr_node, i] += h_rad * obj.area
                # flux indexing (applied at the end of this function, to allow calculation of diagonal of A)
                space_count = 0
                for space in Space_list:
                    for env in space.envelope_list:
                        if env == obj.label:  # we found it
                            radiative_share = space.envelope_list[env]['radiative_share']
                            flux_B_indexing.append([i, index_inputs['space_radiative_gain']['start_index'] + space_count, radiative_share])  # radiative_gain_boundary_external
                    space_count += 1
            # conduction towards next (node = 0) or previous node (node == 1)
            resistance_window = 1 / obj.u_value  # TODO: correct for internal and external heat exchange coefficients !
            u_window_intr = u_value_window(resistance_window, h_rad_ext=5.25, h_rad_int=5.25, h_conv_ext=16.37, h_conv_int=3.16)
            if node == 0:
                A[i, i+1] += u_window_intr * obj.area
            elif node == 1:
                A[i, i-1] += u_window_intr * obj.area
            else:
                pass
            mcp[i] = 1. * obj.area
            i += 1

    for obj in Space_list:  # mean radiant nodes, already filled in in boundaries and windows !
        mcp[i] = obj.volume * cp_air_ref * rho_ref
        i += 1

    n_space = 0
    for obj in Space_list:  # air nodes
        mcp[i] = obj.volume * cp_air_ref * rho_ref
        # flux indexing (applied at the end of this function, to allow calculation of diagonal of A)
        flux_B_indexing.append([i, index_inputs['space_convective_gain']['start_index'] + n_space, 1])  # convective gain to space air node
        i += 1
        n_space += 1

    # calculate diagonal of A with leaving coefficients
    for node in range(n_total_nodes):
        A[node, node] -= np.sum(A[node, :]) + np.sum(B[node, :])

    # add indexes for heat fluxes into B
    for flux in flux_B_indexing:
        B[flux[0], flux[1]] = flux[2]  # connect flux by scaling factor flux[2]

    # correct cp values (are in kJ/kg/K for the moment)
    for node in range(n_total_nodes):
        A[node, :] /= mcp[node]
        B[node, :] /= mcp[node]

    return A, B, index_states, index_inputs
