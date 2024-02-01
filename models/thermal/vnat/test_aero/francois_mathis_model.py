import os
import time
from models.thermal.vnat.test_cases.data_model import t_ext
import pymathis.pymathis as pm
import numpy as np
import math


def create_mathis_datafile(tbegin, dt, branches, noeuds, t_out, mathis_dir, mathis_file):

    # File creation
    Case = pm.CreateFile(mathis_dir, mathis_file)
    # SImulation parameters
    Case = pm.CreateObj(Case, 'MISC', TETA0=tbegin, DTETA=dt, TIMEUNIT='H', BOUSSINESQ=True, NSAVE=0, OUTPUT_MESSAGE_ONLY=True )
    Case = pm.CreateObj(Case, 'EXT',TEXT=t_out )

    for i in noeuds:
        if noeuds[i]['type'] == 'node':
            Case = pm.CreateObj(Case, 'LOC', ID=i, ALT=noeuds[i]['z'], LOCTYPE='ROOM', TINI=noeuds[i]['temperature'], AREA=noeuds[i]['volume']**(2/3), HEIGHT=noeuds[i]['volume']**(1/3))
        else:
            Case = pm.CreateObj(Case, 'BOUND', ID=i, ALT=noeuds[i]['z'], DP=1, DPCTRLID=i+'_pctrl', TBOUND=noeuds[i]['temperature'])
            Case = pm.CreateObj(Case, 'CTRL', ID=i+'_pctrl', CTRLTYPE='PASSIVE')

    for j in branches:
        connection = branches[j]['connection']
        if connection['connection_type'] == 'vent_volume_flow':
            Case = pm.CreateObj(Case, 'BRANCH', ID=j, LOCIDS=[branches[j]['path'][0], branches[j]['path'][1]],
                                Z1=branches[j]['z'] - noeuds[branches[j]['path'][0]]['z'],
                                Z2=branches[j]['z'] - noeuds[branches[j]['path'][1]]['z'],
                                BRANCHTYPE='VENT_VOLUMEFLOW', QV0=connection['flow_rate'])
        elif connection['connection_type'] == 'fan_mechanical':
            np.savetxt(mathis_dir + '/' + j + '_pqfile.txt', np.transpose(connection['pressure_curve']), fmt='%d', delimiter='\t')
            Case = pm.CreateObj(Case, 'BRANCH', ID=j, LOCIDS=[branches[j]['path'][0], branches[j]['path'][1]],
                                Z1=branches[j]['z'] - noeuds[branches[j]['path'][0]]['z'],
                                Z2=branches[j]['z'] - noeuds[branches[j]['path'][1]]['z'],
                                BRANCHTYPE='FAN_MECHANICAL', PQFILE=j + '_pqfile.txt')
        elif connection['connection_type'] == 'duct_dtu':
            Case = pm.CreateObj(Case, 'BRANCH', ID=j, LOCIDS=[branches[j]['path'][0], branches[j]['path'][1]],
                                Z1=branches[j]['z'] - noeuds[branches[j]['path'][0]]['z'],
                                Z2=branches[j]['z'] - noeuds[branches[j]['path'][1]]['z'],
                                BRANCHTYPE='DUCT_DTU',
                                SECTION=connection['section'], DIAM=connection['h_diam'],
                                LENGTH=connection['length'], K=connection['coefK'], SINGU=connection['dzeta'])
        elif connection['connection_type'] == 'door':
            Case = pm.CreateObj(Case, 'BRANCH', ID=j, LOCIDS=[branches[j]['path'][0],branches[j]['path'][1]],
                                Z1=branches[j]['z']-noeuds[branches[j]['path'][0]]['z'],
                                Z2=branches[j]['z']-noeuds[branches[j]['path'][1]]['z'],
                                BRANCHTYPE='ORIFICE', SECTION=connection['section'], COEF=connection['discharge_coefficient'])
        else:
            Case = pm.CreateObj(Case, 'BRANCH', ID=j, LOCIDS=[branches[j]['path'][0], branches[j]['path'][1]],
                                Z1=branches[j]['z']-noeuds[branches[j]['path'][0]]['z'],
                                Z2=branches[j]['z']-noeuds[branches[j]['path'][1]]['z'],
                                BRANCHTYPE='GRILLE_FIXED', DPREF=connection['dp0'], RHOREF=connection['rho0'], QV0=connection['flow0'])
    # closing file
    Case.close()


def pymathis_model(t_final, nodes_init, flow_paths_init, model, apply_dp, dynamic_test):

    flow_paths = flow_paths_init.copy()
    nodes = nodes_init.copy()

    # setting calculation parameters 
    t = 0
    dt = 1

    # Creation du fichier MATHIS
    c_file_path = os.path.join(os.path.dirname(os.getcwd()), 'test_aero/cas_mathis')
    c_file = 'cas'
    create_mathis_datafile(t, dt, flow_paths, nodes, t_ext, c_file_path, c_file)

    # Initialisation du calcul
    os.chdir(c_file_path)
    smartmathis = pm.LoadDll(pm.__file__, c_file+'.data')
    # Initialisation des tableaux résultats
    n_pressure = 0
    for i in nodes:
        if nodes[i]['type'] == 'node':
            n_pressure = n_pressure + 1

    pressure_results = np.zeros((t_final, n_pressure))
    flowrate_results = np.zeros((t_final, len(flow_paths)))

    # boucle temporelle
    while t < t_final:

        node_nb = 0
        for node in nodes:
            if nodes[node]['type'] == 'boundary_condition':
                node_nb += 1
                nodes[node]['pressure'] = nodes[node]['pressure_list'][t]

        # pressure update at boundaries
        k = -1
        for i, id in enumerate(nodes):
            if nodes[id]['type'] == 'boundary_condition':
                k = k+1
                pm.give_passive_ctrl(smartmathis, nodes[id]['pressure'], k)

        # Résolution du pas de temps actuel
        pm.solve_timestep(smartmathis, t*3600, dt*3600)

        # Stockage ds résultats
        # recup debit volumique des branches
        for j, id_branch in enumerate(flow_paths):
            flowrate_results[t, j] = pm.get_obj_value(smartmathis, 'BRANCH', id_branch, 'QV')
        # recup des pressions des noeuds
        k = -1
        for i, id_loc in enumerate(nodes):
            if nodes[id_loc]['type'] == 'node':
                k = k+1
                pressure_results[t, k] = pm.get_obj_value(smartmathis, 'LOC', id_loc, 'DP')

        # Mise à jour de l'heure courante
        t = t + dt

    pm.CloseDll(smartmathis)

    mode_papoter = False
    if mode_papoter:
        print(pressure_results[-1,:])
        print(flowrate_results[-1,:])
        print('CPUtime PyMathis: ', toc - tic)

    for j, flow_path in enumerate(flow_paths):
        flow_paths[flow_path]['flow_rate_mathis'] = flowrate_results[:, j]

# if __name__ == '__main__':
#     test_main()
