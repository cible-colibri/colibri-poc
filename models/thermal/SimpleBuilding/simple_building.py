import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.model import Model
from core.variable import Variable


class SimpleBuilding(Model):

    def __init__(self, name: str):
        self.name = name
        self.inputs = [
            Variable('zone_setpoint_heating', 20.),  # default setpoint heating [°C]
            Variable('zone_setpoint_cooling', 27.),  # default setpoint cooling [°C]
            Variable('wwr', 0.2),  # window wall ration [-]
            Variable('ach', 0.5),  #
            Variable('u_wall', 0.5),
            Variable('u_roof', 0.3),
            Variable('u_floor', 0.25),
            Variable('u_window', 2.5),
            Variable('area_walls_t', 200.),  # total wall area (windows+opac)
            Variable('eta_recup', 0.),
            Variable('area_floor', 50.),
            Variable('nb_floors', 2),
            Variable('trans_window', 0.7),
            Variable('heating', True),
            Variable('cooling', False),
            Variable('ext_temperature', 20),
            Variable('radiation', 0)
        ]
        self.outputs = [
            Variable("outlet_flow_rate"),  # kg/h
            Variable("outlet_temperature"),  # °C
        ]

    def initialize(self):
        self.volume = self.area_floor * self.nb_floors * 2.5

        # calculate opac and window area
        self.area_windows = self.area_walls_t * self.wwr
        self.area_walls = self.area_walls_t * (1 - self.wwr)

        # pre-calculate setpoint for all(!) time steps (heating or cooling default setpoint)
        # this demonstrates how to creates a link to a different model (the weather data model) :
        # this model (the SimpleBuilding) cannot run without it!
        # it is recommended to reduce such dependencies to the minimum
        weather = self.project.get_models('Weather')[0]

        ext_temperature_list = weather.climate_data['temperature']
        self.zone_setpoint_list = np.zeros(len(ext_temperature_list)) + self.zone_setpoint_heating

        self.heating_season = np.empty(len(ext_temperature_list))
        self.heating_on = ext_temperature_list.rolling(48).mean() <= 15
        self.heating_on[0:48] = True
        self.heating_season_list = self.heating_on

        # season calculation simple whenever heating is needed
        if self.cooling:  # replace setpoint for cooling in setpoint_list
            self.zone_setpoint_list[self.heating_season == False] = self.zone_setpoint_cooling


    def run(self, step):
        ext_temperature = self.ext_temperature
        radiation = self.radiation

        zone_setpoint = self.zone_setpoint_list[step]
        heating_season = self.heating_season_list[step]

        self.phi_hvac, self.zone_temperature = model(self.volume, zone_setpoint, self.ach, self.eta_recup,
                                                                 ext_temperature,
                                                                 self.u_window, self.area_windows, self.trans_window,
                                                                 self.area_walls, self.u_wall,
                                                                 self.u_roof,
                                                                 self.area_floor, self.u_floor, self.nb_floors,
                                                                 radiation,
                                                                 heating_season,
                                                                 self.heating, self.cooling)

    def simulation_done(self, time_step=0):
        print(f"{self.name}:")
        # plot_building(1, zone_temperature, phi_hvac, ext_temperature_list, model_type='simplicity', to_plot=True)


def plot_building(id, zone_temperatures, phi_hvacs, ext_temperature, model_type='simplicity', to_plot=False):
    if to_plot:
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(311)
        ax1.plot(zone_temperatures, label='zone_temperature')
        ax1.plot(ext_temperature, label='ext_temperature')
        ax1.set_ylabel('Temperature [degC]')
        ax1.set_title('Building nb - ' + str(id))
        ax1.set_ylim([0, 50])
        ax2 = fig1.add_subplot(312, sharex=ax1)
        ax2.plot(phi_hvacs, label='heating power')
        ax2.set_ylabel('Load [W]')
        ax3 = fig1.add_subplot(313, sharex=ax1)
        ax3.plot(np.cumsum(phi_hvacs / 1000., axis=0), label='heating demand')
        ax3.set_ylabel('Demand [kWh]')
        ax3.set_xlabel('Time [h]')
        plt.show()


# original function provided by the author of the model; keeping it as a separate function will simplify Cythonization
def model(volume, zone_setpoint, ach, eta_recup, ext_temperature, u_window, area_windows, trans_window, area_walls,
          u_wall,
          u_roof, area_floor, u_floor, nb_floors, radiation, heating_season,
          heating, cooling
          ):
    """
    A simplified model to simulate the heating energy demand of a building

    Args:
        zone_setpoint (int): set point temperature of building hvac systems
        ach (float): ventilation air change rate (m3/h)
        area_floor (m2)
        nb_floors
        volume (m3)
        trans_window (% ratio)
        eta_recup (float): Heat recovery efficiency (% ratio)
        ext_temperature (pd.Series): timeseries hourly temperature values for a year period (°C)
        u_window (float): thermal resistance value of windows (W/(m2.K))
        area_windows (float): window surface area (m2)
        area_walls (float): wall surface area (m2)
        u_wall (float): thermal resistance value of walls (W/(m2.K))
        u_roof (float): thermal resistance value of roof (W/(m2.K))
        u_floor (float): thermal resistance value of floor (W/(m2.K))
        radiation (pd.Series): global horizontal radiation hourly values for a year period
            (GloHorzRad in energyPlus weather file format) (W/m2)

    Return:
         (np.array): energy heating demand of building (Wh)
         (np.array): Building temperature (°C)

    Notes:
        1. The simulation is designed to have a one-hour resolution, if another resolution is
            required, some calculations may need to be adapted
    """
    ground_temperature = np.mean(ext_temperature)

    # gains
    blind_pos = np.clip(0.1 + (35 - (ext_temperature + 3)) / (32 - zone_setpoint), 0.1, 1)

    phi_win_gain = area_windows * trans_window * radiation * 0.25 * blind_pos
    phi_gains = area_floor * nb_floors * 10.  # 7 W/m2 0.7 useable floor area
    # losses
    ua_global = ach * volume / 3600. * 1.2 * 1006. * (
                1 - eta_recup) + u_window * area_windows + area_walls * u_wall + area_floor * u_roof
    ua_floor = area_floor * u_floor
    phi_ventilation = ach * volume / 3600. * 1.2 * 1006. * (1 - eta_recup) * (ext_temperature - zone_setpoint)
    phi_win_loss = u_window * area_windows * (ext_temperature - zone_setpoint)
    phi_walls = area_walls * u_wall * (ext_temperature - zone_setpoint)
    phi_roof = area_floor * u_roof * (ext_temperature - zone_setpoint)
    phi_floor = area_floor * u_floor * (ground_temperature - zone_setpoint)
    # heat balance
    phi_hvac = phi_ventilation + phi_win_loss + phi_win_gain + phi_walls + phi_roof + phi_floor + phi_gains
    # post treat for results
    if heating:
        p_h = [0, 1e9]
    else:
        p_h = [0, 0]
    if cooling:
        p_c = [-1e9, 0]
    else:
        p_c = [0, 0]

    if hasattr(phi_hvac, "__len__"):
        phi_hvac[heating_season] = np.clip(-phi_hvac[heating_season], p_h[0], p_h[1])  # heating demand
        phi_hvac[heating_season == False] = np.clip(-phi_hvac[heating_season == False], p_c[0],
                                                    p_c[1])  # cooling demandd
    else:
        if heating_season:
            phi_hvac = np.clip(-phi_hvac, p_h[0], p_h[1])  # heating demand
        if not heating_season:
            phi_hvac = np.clip(-phi_hvac, p_c[0], p_c[1])  # cooling demandd

    # temperature balance from all fluxes
    zone_temperature = (
                                   ua_global * ext_temperature + ua_floor * ground_temperature + phi_win_gain + phi_gains + phi_hvac) / (
                                   ua_global + ua_floor)
    if hasattr(phi_hvac, "__len__"):
        zone_temperature = zone_temperature.rolling(12).mean().fillna(20)

    return phi_hvac, zone_temperature
