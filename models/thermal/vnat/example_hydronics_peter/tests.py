import numpy as np

def press_tests(choice=0,random_length=False):

    # individual pipe segment length
    length = 1000.

    if choice == 0:  # 1 generator, 1 substation. test of pump curve iteration and pressure drop calculation
        nodes = [[0, 0, 0], # [id, x, y]
                 [1, 1, 0],
                 [2, 1, -0.2],
                 [3, 0, -0.2]]

        flow_paths = [[0,1,0],  # [node i, node j, network number (0=supply, 1=return)]
                      [2,3,1]]

        substation_list = [[1,2]]  # [node_i, node_j] - suppy and return nodes
        pump_list = [[3,0]] # [j, i] extract from node j to node i

    ###########################################################################################################
    elif choice == 1:  # 1 generator, 2 substations (for test of balancing)

        nodes = [[0, 0, 0], # [id, x, y]
                 [1, 1, 0],
                 [2, 3, 0],
                 [3, 1, 1],
                 [4, 0, -0.2],
                 [5, 1.2, -0.2],
                 [6, 3, -0.2],
                 [7, 1.2, 1]]

        flow_paths = [[0,1,0, 10.],   # [node i, node j, network number (0=supply, 1=return)]
                      [1,2,0, 10000.],
                      [1,3,0, 10],
                      [4,5,1, 10.],
                      [5,6,1, 10000.],
                      [5,7,1, 10.]]

        substation_list = [[3,7],  # [node_i, node_j] - suppy and return nodes
                           [2,6]]
        pump_list = [[4,0]] # [j, i] extract from node j to node i

    ###########################################################################################################
    elif choice == 2:  # 2 generators, 1 substation. test of multi-injection

        nodes = [[0, 0, 0], # [id, x, y]
                 [1, 1, 0],
                 [2, 3, 0],
                 [3, 1, 1],
                 [4, 0, -0.2],
                 [5, 1.2, -0.2],
                 [6, 3, -0.2],
                 [7, 1.2, 1]]

        flow_paths = [[0,1,0],   # [node i, node j, network number (0=supply, 1=return)]
                      [1,2,0],
                      [1,3,0],
                      [4,5,1],
                      [5,6,1],
                      [5,7,1]]

        substation_list = [[3,7]]  # [node_i, node_j] - suppy and return nodes
        pump_list = [[4,0], # [j, i] extract from node j to node i
                     [6,2]]

    ###########################################################################################################
    elif choice == 3:  # 3 generators, 3 substations; tri-tube tests

        nodes = [[0, 0, 2.2], # [id, x, y]
                 [1, 1, 2.2],
                 [2, 3.2, 2.2],
                 [3, 3.5, 2.2],
                 [4, 4.2, 2.2],
                 [5, 4.2, 1],
                 [6, 3.2, 1],
                 [7, 1, 3],
                 [8, 3.5, 3],
                 [9, 5.2, 2.2],
                 [10, -0.3, 2],
                 [11, 1.5, 2],
                 [12, 2.8, 2],
                 [13, 1.5, 3],
                 [14, 2.8, 3],
                 [15, 5.4, 2],
                 [16, 0, 2.4],
                 [17, 3, 2.4],
                 [18, 4, 2.4],
                 [19, 3, 1.2],
                 [20, 4, 1.2],
                 [21, 5.2, 2.4],
                 [22, 2, 1.2],
                 [23, 5, 1.2],
                 [24,2,1],
                 [25,5,1]]

        flow_paths = [[0,1,0],   # [node i, node j, network number (0=supply1, 1=supply2, 2=return)]
                      [1,2,0],
                      [1,7,0],
                      [2,3,0],
                      [2,6,0],
                      [3,8,0],
                      [3,4,0],
                      [4,5,0],
                      [4,9,0],
                      [5,6,0],
                      [5,25,0],
                      [6,24,0],
                      [10,11,1],
                      [11,12,1],
                      [11,13,1],
                      [12,14,1],
                      [12,15,1],
                      [16,17,2],
                      [17,18,2],
                      [17,19,2],
                      [18,20,2],
                      [18,21,2],
                      [19,20,2],
                      [20,23,2],
                      [19,22,2]]

        substation_list = [[7,13],  # [node_i, node_j] - suppy and return nodes
                           [9,15],
                           [21,15],
                           [23,25]]

        pump_list = [[10,0], # [j, i] extract from node j to node i
                     [10,16],
                     [14,8],
                     [24,22]]

    else:
        print('This test is not defined')

    nnodes = len(nodes)
    LL = np.zeros((nnodes, nnodes))
    for conn in flow_paths:  # connect paths in length matrix
        if random_length:
            delta_L = length/2. + np.random.random()*length
        else:
            delta_L = length/2.

        length_act = length/2. + delta_L
        LL[conn[0], conn[1]] = length_act + conn[-1]
        LL[conn[1], conn[0]] = length_act + conn[-1]
    # add connnections in substations
    for sub in substation_list:
        LL[sub[0], sub[1]] = 0.05#length  # use for the moment the same pressure coeffients as tubes in segments
        LL[sub[1], sub[0]] = 0.05#length


    return LL, nnodes, flow_paths, nodes, pump_list, substation_list