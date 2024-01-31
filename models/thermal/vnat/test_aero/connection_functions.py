import numpy as np
import time
from vnat.test_aero.generic_functions import interpolate_function


def door_calculate_kb(section=2, discharge_coefficient=0.6, opening=1):
    kb = discharge_coefficient * section * opening * 2**0.5
    return kb


def grille_calculate_kb(dp0=20, rho0=1.2, flow0=0.5, n=0.5, opening=1):
    kb = opening * flow0/3600. / dp0**n / rho0**(n-1)
    return kb


def fan_mechanical_calculate_dploss(flowrate=45, dplaw=[[0, 45, 100], [80, 80, 0]]):
    # dp from interpolation between data points
    # dplaw[0] : input list with flow rates passing the fan
    # dplaw[1] : output list with pressure gains from fan
    # law is based on the characteristic fan curve dp = f(flowrate)
    # dp = -interpolate_function(flowrate, dplaw)  # does not work for the moment !!!
    flowgood = max(0., flowrate)
    for i,value in enumerate(dplaw[0]):
        if dplaw[0][i] <= flowgood:
            j = i
    dp = -(dplaw[1][j]+(flowgood-dplaw[0][j]) / (dplaw[0][j+1]-dplaw[0][j]) * (dplaw[1][j+1]-dplaw[1][j]))
    return dp


def duct_dtu_calculate_dploss(flowrate=45, rho=1.2, section=0.005, h_diam=0.08, length=1, coefK=3.e6, dzeta=[0, 0], calc_mode='pressure'):
    # original function Francois
    # dp = (flowrate/abs(flowrate))*(coefK*length*abs(flowrate)**1.9/(1000*h_diam)**5+singu*0.5*rho*(flowrate/3600/section)**2)
    # dp = sign * (C1  * flowrate**1.9 + C2 * flowrate**2)

    if flowrate == 0:
        dp = 0
        return dp
    else:
        if flowrate > 0:
            singu =  dzeta[0]
        else:
            singu = -dzeta[1]

        c1 = coefK * length / (1000 * h_diam) ** 5
        c2 = singu * 0.5 * rho * (1 / 3600 / section) ** 2

        if calc_mode == 'pressure':
            dp = np.sign(flowrate) * (c1 * np.abs(flowrate) ** 1.9 + c2 * flowrate ** 2)
            return dp
        elif calc_mode == 'c_lin':  # convert to quadratic function for matrix air flow calculation
            c_lin = 1 / (c1 + c2)
            return c_lin
        else:
            raise ValueError('wrong parameter for calculation type in duct model')
