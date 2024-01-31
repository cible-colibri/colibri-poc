import numpy as np
import vnat.test_aero.connection_functions as cf
import random

def bilan_total(x, n_pressure, nodes, n_special, flow_paths, rho_ref, t_ref, calc_type='solve'):

    # criteria for linearisation

    reynolds_crit = 500

    # initialisation des bilans

    bilan_masse = np.zeros(n_pressure)
    bilan_pressure=np.zeros(n_special)
    bilan = np.zeros(n_pressure+n_special)
    mflow = np.zeros(len(flow_paths))
    # mise à jour des pressions des noeuds
    dp = dict()
    ip_dp = dict()
    k = 0
    for i in nodes:
        if nodes[i]['type'] == 'node':
            dp[i] = x[k]
            ip_dp[i] = k
            k = k+1
        else:
            dp[i] = nodes[i]['pressure']

    dp_flow = np.zeros(len(flow_paths))

    j_special=-1
    for j, flow_path in enumerate(flow_paths):
        # mise à jour de la pression motrice de la branche
        kfrom = flow_paths[flow_path]['path'][0]
        kto = flow_paths[flow_path]['path'][1]
        # buoyant rho  with boussinesq linear approximation
        #rhofrom=rho_ref * (1 - (nodes[kfrom]['temperature']-t_ref)/(t_ref+273.15))
        #rhoto=rho_ref * (1 - (nodes[kto]['temperature']-t_ref)/(t_ref+273.15))
        # buoyant rho with exact calculation using perfect gaz law (same as Mathis)
        rhofrom=101300 / (287 * (273.15 + nodes[kfrom]['temperature']))
        rhoto = 101300 / (287 * (273.15 + nodes[kto]['temperature']))
        correction = - (rhofrom-rhoto) * 9.81 * flow_paths[flow_path]['z']
        # adding buoyancy term to pressure flow
        dp_flow[j] = dp[kfrom]-dp[kto] + correction
        connection = flow_paths[flow_path]['connection']
        #branches with fixed flowrate
        if connection['connection_type'] == 'vent_volume_flow':
            mflow[j]=rho_ref*connection['flow_rate']/3600
        elif (connection['connection_type'] == 'fan_mechanical' or connection['connection_type'] == 'duct_dtu'):
            #branches with pressure gain or loss model as function of flowrate
            j_special += 1
            mflow[j] = x[n_pressure+j_special]
            if connection['connection_type'] == 'fan_mechanical':
                dp_loss=cf.fan_mechanical_calculate_dploss(flowrate=mflow[j]*3600/rho_ref, dplaw=connection['pressure_curve'])
            elif connection['connection_type'] == 'duct_dtu':
                dp_loss=cf.duct_dtu_calculate_dploss(flowrate=mflow[j]*3600/rho_ref, rho=rho_ref, section=connection['section'], h_diam=connection['h_diam'], length=connection['length'], coefK=connection['coefK'], dzeta=connection['dzeta'],calc_mode='pressure')
                # linearization for small flowrates
                qcrit=reynolds_crit*18.6e-6*connection['section']/connection['h_diam']
                if np.abs(mflow[j])<qcrit:
                    dp_try=cf.duct_dtu_calculate_dploss(flowrate=np.sign(mflow[j])*qcrit*3600/rho_ref, rho=rho_ref, section=connection['section'], h_diam=connection['h_diam'], length=connection['length'], coefK=connection['coefK'], dzeta=connection['dzeta'],calc_mode='pressure')
                    dp_try=np.abs(dp_try)
                    dp_loss = dp_try*mflow[j]/qcrit

            bilan_pressure[j_special]=dp_flow[j]-dp_loss

        else:
            # passive branches with flowrate model as function of pressure loss
            if connection['connection_type'] == 'door':
                kb = cf.door_calculate_kb(section=connection['section'], discharge_coefficient=connection['discharge_coefficient'], opening=1)
            else:
                kb = cf.grille_calculate_kb(dp0=connection['dp0'], rho0=connection['rho0'], flow0=connection['flow0'], n=connection['n'], opening=1)

            # linearization for small pressure drop
            if kb > 0:
                dp_crit = max(0.01, ((reynolds_crit*18.6e-6/kb**0.5)**(1/connection['n']))/rho_ref)
            else:
                dp_crit=0.01
            if abs(dp_flow[j]) >= dp_crit:
                mflow[j] = np.sign(dp_flow[j]) * kb * abs(rho_ref*dp_flow[j])**connection['n']
            else:
                mflow[j] = kb * abs(rho_ref*dp_crit)**connection['n'] * dp_flow[j]/dp_crit

        # mass balance update
        if nodes[kfrom]['type'] == 'node':
            bilan_masse[ip_dp[kfrom]] = bilan_masse[ip_dp[kfrom]]-mflow[j]
        if nodes[kto]['type'] == 'node':
            bilan_masse[ip_dp[kto]] = bilan_masse[ip_dp[kto]] + mflow[j]

    bilan[0:n_pressure]=bilan_masse
    bilan[n_pressure:n_pressure+n_special]=bilan_pressure
    if calc_type == 'solve':
        return bilan  # for pressure solving, output flow balance on each node
    else:
        return mflow  # for standard calculation, output mass flow (kg/s) in each branch