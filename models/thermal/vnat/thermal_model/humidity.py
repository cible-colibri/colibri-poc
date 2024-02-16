# -*- coding: utf-8 -*-
# quelques couleurs
rouge_A = '#C60C2E'
vert1_A = '#005157'
vert2_A = '#627D77'
vert3_A = '#9EB28F'
vert4_A = '#C5E5A4'
gris1_A = '#595A5C'
coule = [rouge_A, vert1_A, vert2_A, vert3_A, vert4_A, gris1_A]
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from tqdm import tqdm

import time

start_time = time.time()


############################################################
#
#	Thermophysical functions
#
# vapour pressure at saturation
def fc_pvsat(T):
    return np.power(10, 7.625 * T / (241 + T) + 2.7877)


# vapour diffusivity depending on water content
def fc_deltav(w):
    a = 1.1 * 1e-7
    b = -1.57 * 1e-7
    return a + b * w


# thermal conductivity depending on water content
def fc_lambda(w):
    a = 0.23
    b = 6
    return a + b * w


# sorption curve
def fc_w_phi(phi):
    a = 700  # 1000
    b = 250 * 1e-6  # 146*1e-6
    c = 2.9  # 1.59
    res = a / np.power(1 - np.log(phi / 100) / b, 1 / c)
    return res * 1e-3


# sortpion curve the other way around
def fc_phi_w(w):
    a = 700  # 1000
    b = 250 * 1e-6  # 146*1e-6
    c = 2.9  # 1.59
    phi = np.zeros(len(w))
    phi = np.exp(b * (1 - np.power((a / (1000 * w)), c))) * 100
    return phi


# update local Fourier
def update_Fo(w_vec, k, rho, Cp, dt, dx):
    k = fc_lambda(w)  # variable properties
    Cp_vec = Cp + w_vec / rho
    Fo_vec = k / rho / Cp_vec * dt / dx ** 2
    return Fo_vec


# update local mass Fourier
def update_Fow(w_vec, dt, dx):
    deltav = fc_deltav(w)  # variable properties
    Fow = deltav * dt / dx ** 2
    return Fow


# update local Fourier
def update_Cm(w, phi, T):
    epsilon = 0.001 * np.min(w)
    wp = w + epsilon
    phip = fc_phi_w(wp)
    dw = abs(wp - w)
    dphi = abs(phip - phi) / 100
    pvs = fc_pvsat(T)
    Cm = dw / dphi / pvs
    return Cm


############################################################
#
#	Equation solving
#
def fc_coupled_HAM(vec_Tpvp, vec_Tpv, K, Fo, Fow, dt, rho, Cp, Cm, Lv):
    # split array
    n = int(len(vec_Tpv) / 2)  # half index
    T, pv = vec_Tpv[0:n], vec_Tpv[n:]
    Tp, pvp = vec_Tpvp[0:n], vec_Tpvp[n:]
    # we need phi in order to actualise w
    phi = pv / fc_pvsat(T) * 100
    # compute w
    w = fc_w_phi(phi)
    # update the properties
    Cm = update_Cm(w, phi, T)
    Fo = update_Fo(w, k, rho, Cp, dt, dx)
    Fow = update_Fow(w, dt, dx)
    # Crank-Nicolson scheme
    # explicit and implicit parts for T
    exp_T = 0.5 * (Fo * np.dot(K, T) + Lv * Fow / (rho * Cp) * np.dot(K, pv))
    imp_T = 0.5 * (Fo * np.dot(K, Tp) + Lv * Fow / (rho * Cp) * np.dot(K, pvp))
    T_term = -Tp + T + exp_T + imp_T
    # explicit and implicit parts for pv
    exp_pv = 0.5 * (Fow / Cm * np.dot(K, pv))
    imp_pv = 0.5 * (Fow / Cm * np.dot(K, pvp))
    pv_term = -pvp + pv + exp_pv + imp_pv
    # send back as one array
    return np.hstack([T_term, pv_term])

# domain size
n_solid = 15
n = n_solid + 2
L = 0.1  # m
# heat transfer matrix
K = np.eye(n, n, k=-1) * 1 + np.eye(n, n) * -2 + np.eye(n, n, k=1) * 1
K[0, 0], K[0, 1], K[-1, -1], K[-1, -2] = 0, 0, 0, 0

#####################
# Time & storage
t = 0
dt = 60
period = 1  #
period_sec = period * 3600
nb_period = 30  #
sim_time = nb_period * 60  # seconds
modulo_storage = 1#int(nb_period * 60)  # sim_time/dt/100
# preparing post-process
store_Text, store_pvext = [], []
store_w, store_phi, store_T, store_pv = [], [], [], []
# arrays
pv, dw, w, T = np.ones(n), np.ones(n), np.ones(n), np.ones(n)

# physical props
Lv = 2400 * 1e3  # J/kg
k = 1.6
rho = 2800
Cp = 1000
alpha = k / rho / Cp  # 1e-7 #m2/s
dx = L / (n_solid)  #
Fo = alpha * dt / dx ** 2
# boundary conditions
Tleft = 20
pvleft = 1200
Tright = Tleft
pvright = pvleft
# initial conditions
pv_init = np.ones(n) * 1000
T_init = np.ones(n) * 15
pv = pv_init
T = T_init
phi = pv / fc_pvsat(T) * 100
w = fc_w_phi(phi)
w_init = w
phi_init = phi

Cm = update_Cm(w, phi, T)
Fo = update_Fo(w, k, rho, Cp, dt, dx)
Fow = update_Fow(w, dt, dx)
i = 0
pbar = tqdm(total=sim_time)  # set up a progress par
# time loop
while t <= sim_time:
    # update boundary conditions
    T[0] = Tleft
    T[-1] = Tleft + 20*0
    pv[0] = pvleft
    pv[-1] = pvleft + 300*0

    # solve the coupled, non-linear system
    result_array = fsolve(fc_coupled_HAM,
                          np.hstack([T, pv]),
                          args=(np.hstack([T, pv]), K, Fo, Fow, dt, rho, Cp, Cm, Lv))

    # split the result into T and pv
    T_plus, pv_plus = result_array[0:n], result_array[n:]

    # compute phi
    phi = pv / fc_pvsat(T) * 100
    # compute water content
    w = fc_w_phi(phi)

    # do some storage for plotting
    if (int(t) % modulo_storage) == 0 and t != 0:
        store_w.append(w[1:-1] * 1000)
        store_phi.append(phi[1:-1])
        store_T.append(T[1:-1])
        store_pv.append(pv[1:-1])
    # update variables
    pv = pv_plus
    T = T_plus
    t += dt
    i += 1
    pbar.update(dt)  # update progress bar
pbar.close()  # close it

elapsed_time = (time.time() - start_time)  # in seconds
print('computational effort ', round(elapsed_time / (sim_time / 3600), 2), ' [seconds/hour simulation]')
print('elapsed time :', round(elapsed_time / 3600), 'h', round((elapsed_time % 3600) / 60), 'min')
x_pos = np.arange(int(L / dx) + 2) * dx
x_pos = x_pos - dx / 2
x_pos = x_pos[1:-1]

print("\n#################\nPlotting (can be long)")
stop = int(len(store_phi))
start = 0
############################################################
##############################
plt.subplot(121)
plt.xlabel("x position [m]")
plt.ylabel(r"$\varphi$ [%]")
plt.plot(x_pos, phi_init[1:-1], '--', color=coule[1], alpha=0.5)
for i in range(start, stop):
    plt.plot(x_pos, store_phi[i], '-', color=coule[1], alpha=0.35)

plt.subplot(122)
plt.xlabel("x position [m]")
plt.ylabel("water content [g/m$^3$]")
plt.plot(x_pos, w_init[1:-1] * 1000, '--', color=coule[3], alpha=0.5)
for i in range(start, stop):
    plt.plot(x_pos, store_w[i], '-', color=coule[3], alpha=0.15)

plt.tight_layout()
plt.show()
# plt.savefig("./graph_duo_phi_w.pdf")


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


def pvsat(temperature):
    # vapour pressure at saturation
    # T in °C
    # output: saturation pressure in Pa
    return np.power(10, 7.625 * temperature / (241 + temperature) + 2.7877)


# sortpion curve the other way around
def calc_sorption_curve_humidity_from_water_content(water_content):
    # a = 1000  # brick
    # b = 146*1e-6  # brick
    # c = 1.59  # brick
    a = 700  # 1000
    b = 250 * 1e-6  # 146*1e-6
    c = 2.9  # 1.59
    humidity = np.exp(b * (1 - (a / (water_content*1000)) ** c)) * 100
    return humidity


def calc_sorption_curve_water_content_from_humidity(humidity):
    a = 1000  # brick
    b = 146*1e-6  # brick
    c = 1.59  # brick
    res = a / ((1 - np.log(humidity / 100) / b) ** 1 / c)
    return res


def calc_air_permeability(temperature, absolute_pressure):
    # temperature [degC]
    # absolute pressure [Pa]
    return 1.97 * 10**(-7) * ((temperature+273)**0.81) / absolute_pressure


def calc_permeability(my, temperature, absolute_pressure):
    air_permeability = calc_air_permeability(temperature, absolute_pressure)
    return air_permeability / my


def calc_permeance(water_content, thickness, permeance_0=1.1e-7):
    # vapour diffusivity depending on water content: delta_V / Thickness
    # parameters correspond to "spruce" (epicea in french)
    # delta_v (permeance) = permeance_0 + b * water_content
    b = -1.57e-7  # impact of water content on permeance
    return (permeance_0 + b * water_content) / thickness


def calc_Sd(my, thickness):
    return my * thickness


def calc_my(Sd, thickness):
    return Sd / thickness


def calc_Cm(water_content, relative_humidity, temperature, thickness, density):
    # calculates CM from d_water_content / d_humidity / saturation_pressure
    delta_water_content = abs(0.01 * np.min(water_content))  # 0.1% of minimum water content change
    relative_humidity_2 = calc_sorption_curve_humidity_from_water_content(water_content + delta_water_content)
    delta_relative_humidity = abs(relative_humidity_2 - relative_humidity) / 100
    saturation_pressure = pvsat(temperature)
    Cm = delta_water_content / delta_relative_humidity / saturation_pressure * thickness * density
    return Cm


# base equation:
"""
gv : water flow rate [kg/s]
permeability: permeability [kg/(m * s * Pa)] or [s] also called delta_p (greek letters)
wp: permeance [kg/(m² * s * Pa] : permeability / thickness
rd: resistance to diffusion [m2*s*Pa/kg] = 1/wp
my: permeability rate compared to air layer [-] = permeability_air / permeability_material (big my = small resistance to diffusion)
thick: thickness of layer
Sd: thickness of equivalent air layer [m] - high value = high diffusion resistance 
pv: water vapor pressure [Pa]
Cm: moisture storage capacity [kg_w / kg / K]

Example: insulation layer with 100mm thickness and my of 1.3
--> sd = my * thick = 1.3 * 0.1m = 0.13m
Cm * dpv_i/dt = wp * (pj - pi)

"""
from collections import namedtuple


def gen_wall_model(boundary):
    # generates the resistances between all nodes in all layers of a boundary (wall, ceiling, floor)
    # input is either a class instance or a Namedtuple "boundary"

    # load properties
    thickness = boundary.thickness
    permeance_0 = boundary.permeance_0
    discret = boundary.discret  # number of layer discretisation

    # calc_Cm(water_content, relative_humidity, temperature, thickness, density)

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


nnodes = 5
temperature_list = np.random.random(nnodes) * 1 + 20.#np.zeros(nnodes) + 20.
water_content_list = np.zeros(nnodes) + 1e-1
rel_humidity_list = calc_sorption_curve_humidity_from_water_content(water_content_list)
# Cm = np.zeros(len(water_content_list))
Cm = calc_Cm(water_content_list, rel_humidity_list, temperature_list)

# create A and B matrices
# fill in with wp values
# Cm * dpv_i/dt = wp * (pj - pi)
# A indexes = wp(i) / Cm(i)

bound_param_list = ['thickness', 'permeance', 'discret']
Boundary = namedtuple('Boundary', bound_param_list)
calc_Cm(water_content, relative_humidity, temperature, thickness, density)
Boundary.water_content = 50/1000.
Boundary.relative_humidity = 20.
Boundary.temperature = 20.
Boundary.thickness = 0.1
Boundary.density = 1000.
permeance = fc_deltav(water_content_list)

