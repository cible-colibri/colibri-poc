"""
Module of the simplified building, kept separated for possible Cythonization.
"""

from typing import Tuple, Union

import numpy as np
from pandas import Series


def simplified_building_model(
    air_change_rate: float,
    area_floor: float,
    area_walls: float,
    area_windows: float,
    exterior_air_temperature: Union[float, Series],
    floor_specific_thermal_conductance: float,
    global_horizontal_radiation: Union[float, Series],
    heating_season: Union[bool, Series],
    heat_recovery_efficiency: float,
    is_cooling_on: bool,
    is_heating_on: bool,
    number_of_floors: int,
    roof_specific_thermal_conductance: float,
    volume: float,
    wall_specific_thermal_conductance: float,
    window_specific_thermal_conductance: float,
    window_transmission: float,
    zone_setpoint_temperature: int,
) -> Tuple[Union[float, Series], Union[float, Series]]:
    """Simplified model to simulate the heating energy demand of a building

    Parameters
    ----------
    air_change_rate : float
        Ventilation air change rate (ACH) [m³/h]
    area_floor : float
        Total surface area of the floor [m²]
    area_walls : float
        Total surface area of the walls [m²]
    area_windows : float
        Total surface area of the windows [m²]
    exterior_air_temperature : Unioon[float, Series]
        Hourly temperatures for a year or at a specific hour [°C]
    floor_specific_thermal_conductance : float
        Specific thermal conductance of the floor [W/(m².K)]
    global_horizontal_radiation : Union[float, Series]
        Hourly global horizontal radiation for a year or at a specific hour [W/m2]
        (GloHorzRad in energyPlus weather file format)
    heating_season: Union[bool, Series]
        Heating season [-]
    heat_recovery_efficiency : float
        Heat recovery efficiency for ventilation [%]
    is_cooling_on : bool
        Specify whether or not the cooling system is on
    is_heating_on : bool
        Specify whether or not the heating system is on
    number_of_floors : int
        Number of floors [-]
    roof_specific_thermal_conductance : float
        Specific thermal conductance of the roof [W/(m².K)]
    volume : float
        Volume of the zone [m³]
    wall_specific_thermal_conductance : float
        Specific thermal conductance of the walls [W/(m².K)]
    window_specific_thermal_conductance : float
        Specific thermal conductance of the windows [W/(m².K)]
    window_transmission : float
        Transmission through windows [%]
    zone_setpoint_temperature : int
        Set point temperature of building HVAC systems [°C]

    Returns
    -------
    Tuple[Union[float, Series], Union[float, Series]]
        total_heat_balance : Union[float, np.ndarray]
            Energy heating or cooling demand of the building [Wh]
        zone_temperature : Union[float, np.ndarray]
            Building temperature [°C]

    Raises
    ------
    None

    Notes
    -----
        1. The simulation is designed to have a one-hour resolution,
           if another resolution is required, some calculations may
           need to be adapted

    Examples
    --------
    >>> None
    """
    ground_temperature: np.ndarray = np.mean(exterior_air_temperature)
    # Gains
    blind_positions: np.ndarray = np.clip(
        0.1
        + (35 - (exterior_air_temperature + 3))
        / (32 - zone_setpoint_temperature),
        0.1,
        1,
    )
    gains_through_windows: np.ndarray = (
        area_windows
        * window_transmission
        * global_horizontal_radiation
        * 0.25
        * blind_positions
    )
    floor_gains: float = (
        area_floor * number_of_floors * 10.0
    )  # 7 W/m², 0.7 usable floor area
    # Losses
    global_thermal_conductance: float = (
        air_change_rate
        * volume
        / 3600.0
        * 1.2
        * 1006.0
        * (1 - heat_recovery_efficiency)
        + window_specific_thermal_conductance * area_windows
        + area_walls * wall_specific_thermal_conductance
        + area_floor * roof_specific_thermal_conductance
    )
    floor_thermal_conductance: float = (
        area_floor * floor_specific_thermal_conductance
    )
    ventilation_losses: float = (
        air_change_rate
        * volume
        / 3600.0
        * 1.2
        * 1006.0
        * (1 - heat_recovery_efficiency)
        * (exterior_air_temperature - zone_setpoint_temperature)
    )
    windows_losses: float = (
        window_specific_thermal_conductance
        * area_windows
        * (exterior_air_temperature - zone_setpoint_temperature)
    )
    walls_losses: float = (
        area_walls
        * wall_specific_thermal_conductance
        * (exterior_air_temperature - zone_setpoint_temperature)
    )
    roof_losses: float = (
        area_floor
        * roof_specific_thermal_conductance
        * (exterior_air_temperature - zone_setpoint_temperature)
    )
    floor_losses: float = (
        area_floor
        * floor_specific_thermal_conductance
        * (ground_temperature - zone_setpoint_temperature)
    )
    # Heat balance
    total_heat_balance: Union[float, np.ndarray] = (
        ventilation_losses
        + windows_losses
        + gains_through_windows
        + walls_losses
        + roof_losses
        + floor_losses
        + floor_gains
    )
    # Maximum power (post-treatment)
    min_max_heating_powers = [0, 1e9] if is_heating_on else [0, 0]
    min_max_cooling_powers = [-1e9, 0] if is_cooling_on else [0, 0]
    if hasattr(total_heat_balance, "__len__"):
        # Heating demand
        total_heat_balance[heating_season] = np.clip(
            -total_heat_balance[heating_season],
            min_max_heating_powers[0],
            min_max_heating_powers[1],
        )
        # Cooling demand
        total_heat_balance[heating_season == False] = np.clip(
            -total_heat_balance[heating_season == False],
            min_max_cooling_powers[0],
            min_max_cooling_powers[1],
        )
    else:
        # Heating demand
        if heating_season:
            total_heat_balance = np.clip(
                -total_heat_balance,
                min_max_heating_powers[0],
                min_max_heating_powers[1],
            )
        # Cooling demand
        if not heating_season:
            total_heat_balance = np.clip(
                -total_heat_balance,
                min_max_cooling_powers[0],
                min_max_cooling_powers[1],
            )
    # Temperature balance from all fluxes
    zone_temperature: Union[float, np.ndarray] = (
        global_thermal_conductance * exterior_air_temperature
        + floor_thermal_conductance * ground_temperature
        + gains_through_windows
        + floor_gains
        + total_heat_balance
    ) / (global_thermal_conductance + floor_thermal_conductance)
    if hasattr(total_heat_balance, "__len__"):
        zone_temperature = zone_temperature.rolling(12).mean().fillna(20)
    return total_heat_balance, zone_temperature
