import numpy as np
from models.thermal.vnat.example_hydronics_peter.pressure_functions import calc_tube
from models.thermal.vnat.example_hydronics_peter.constants import tube_base
from models.thermal.vnat.example_hydronics_peter.pump_functions import pump, pump_chars
import matplotlib.pyplot as plt
import time


material = 0
k = tube_base['pipe_roughness'][material]
flowrate = 3./60.
outlet_pressure = 2.2*1e4
pump_speed_nominal = 1500.
pump_speed = 800.
lambada = 0.0316
lambada0 = 0.01
diameter_internal = 0.009
tube_length = 10.
inlet_temperature = 30.
pressure_drop = 10000.
pressure_drop_0 = 0.
inlet_pressure = pressure_drop
pump_data_table = pump_chars()
threshold = 1e-5  # pressure in Pa
iter_max = 50
start = time.time()

toplot = True
if toplot:
    plt.ion()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
else:
    fig=ax1=ax2 = []

for ts in range(24):
    not_converged = True
    n_iter = 0
    pump_speed = 1200. + np.random.random()*600.
    T = 40. + np.random.random()*20.
    while not_converged:
        flowrate, pump_power, fig, ax1 = pump(flowrate, inlet_pressure, pump_speed, pump_data_table, pump_speed_nominal,toplot, iter_max, fig, ax1, pump_efficiency=0.25)
        pressure_drop, lambada, velocity = calc_tube(diameter_internal, tube_length, inlet_temperature, flowrate, lambada, k, share_singular=0.5)
        inlet_pressure =  -pressure_drop
        delta = np.abs(lambada0-lambada)
        if (delta<=threshold) or (n_iter > iter_max):
            not_converged = False
            print("step {:3.0f} / n_iter {:3.0f} : inlet_pressure: {:8.1f} Pa - fluid velocity: {:5.2f} m/s - flowrate: {:5.2f} l/min - pump_power: {:5.1f} W - lambada {:5.4f}".format(ts, n_iter, -inlet_pressure, velocity, flowrate * 60., pump_power, lambada))
        lambada0 = lambada
        n_iter += 1

print("simulation time: {:3.2f} seconds".format(time.time()-start))
