# SimpleBuilding en standalone pour mésurer l'overhead de l'environnement
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Save starting time
starting_time = time.perf_counter()


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
        ax3.plot(np.cumsum(phi_hvacs/1000., axis=0), label='heating demand')
        ax3.set_ylabel('Demand [kWh]')
        ax3.set_xlabel('Time [h]')
        plt.show()

def import_epw_weather(epw_path = "C:\home\source\colibrisuce\data\weather\EnergyPlus\Paris.epw"):
    EPW_vars = ('year', 'month', 'day', 'hour', 'minute', 'datasource', 'temperature', 'DewPoint',
                'RelHum', 'pressure', 'ExtHorzRad', 'ExtDirRad', 'HorzIRSky', 'GloHorzRad', 'direct_radiation',
                'diffuse_radiation', 'GloHorzIllum', 'DirNormIllum', 'DifHorzIllum',
                'ZenLum', 'wind_direction', 'wind_speed', 'TotSkyCvr', 'OpaqSkyCvr', 'Visibility', 'Ceiling',
                'presweathobs', 'presweathcodes', 'precipwtr', 'aerosoloptdepth', 'snowdepth',
                'dayslastsnow', 'albedo', 'rain', 'rain_hr')
    climate_data    = pd.read_csv(epw_path, skiprows=8, header=None, names=EPW_vars)
    radiation       = climate_data['GloHorzRad']
    ext_temperature = climate_data.temperature
    # solar radiation processor every n degrees
    # pv lib
    # radiation_every_ndegrees =  ...
    return radiation, ext_temperature #radiation_every_ndegrees


def model(zone_setpoint,ach,eta_recup,ext_temperature,u_window,area_windows,area_walls,u_wall,u_roof,u_floor,radiation,heating_season):
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
    ua_global = ach * volume / 3600. * 1.2 * 1006. * (1 - eta_recup) + u_window * area_windows + area_walls * u_wall + area_floor * u_roof
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
        phi_hvac[heating_season == False] = np.clip(-phi_hvac[heating_season == False], p_c[0], p_c[1])  # cooling demandd
    else:
        if heating_season:
            phi_hvac = np.clip(-phi_hvac, p_h[0], p_h[1])  # heating demand
        if not heating_season:
            phi_hvac = np.clip(-phi_hvac, p_c[0], p_c[1])  # cooling demandd

    # temperature balance from all fluxes
    zone_temperature = (ua_global * ext_temperature + ua_floor * ground_temperature + phi_win_gain + phi_gains + phi_hvac) / (ua_global + ua_floor)
    if hasattr(phi_hvac, "__len__"):
        zone_temperature = zone_temperature.rolling(12).mean().fillna(20)

    return phi_hvac, zone_temperature

# load weather data from epw
epw_path = "C:\home\source\colibrisuce\config\data\weather\epw\Paris.epw"
radiation_list, ext_temperature_list = import_epw_weather(epw_path)

# thermal zone parameter declaration
zone_setpoint_heating = 20. # default setpoint heating [°C]
zone_setpoint_cooling = 27. # default setpoint cooling [°C]
wwr = 0.2 # window wall ration [-]
ach = 0.5 #
u_wall = 0.5
u_roof = 0.3
u_floor = 0.25
u_window = 2.5
area_walls_t = 200.  # total wall area (windows+opac)
eta_recup = 0.
area_floor = 50.
nb_floors = 2
volume = area_floor * nb_floors * 2.5
trans_window = 0.7
heating = True
cooling = False
# calculate opac and window area
area_windows = area_walls_t * wwr
area_walls = area_walls_t * (1 - wwr)

# calculate setpoint for all time steps (heating or cooling default setpoint)
zone_setpoint_list = np.zeros(len(ext_temperature_list)) + zone_setpoint_heating
# season calculation simple whenever heating is needed
heating_season = np.empty(len(ext_temperature_list))
heating_on = ext_temperature_list.rolling(48).mean() <= 15
heating_on[0:48] = True
heating_season_list = heating_on
if cooling:  # replace setpoint for cooling in setpoint_list
    zone_setpoint_list[heating_season == False] = zone_setpoint_cooling
matrix_calculation = True

if matrix_calculation:
    zone_setpoint = zone_setpoint_list
    phi_hvac, zone_temperature = model(zone_setpoint, ach, eta_recup, ext_temperature_list, u_window, area_windows,area_walls, u_wall, u_roof, u_floor, radiation_list,heating_season_list)
else:
    phi_hvac = np.empty(len(ext_temperature_list))
    zone_temperature = np.empty(len(ext_temperature_list))

    for step in range(len(ext_temperature_list)):
        zone_setpoint = zone_setpoint_list[step]
        ext_temperature = ext_temperature_list[step]
        radiation = radiation_list[step]
        heating_season = heating_season_list[step]
        phi_hvac[step], zone_temperature[step] = model(zone_setpoint, ach, eta_recup, ext_temperature, u_window, area_windows,
                                           area_walls, u_wall, u_roof, u_floor, radiation,heating_season)

plot_building(1, zone_temperature, phi_hvac, ext_temperature_list, model_type='simplicity', to_plot=True)

print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")
