"""
SimpleBuilding class from ThermalSpace interface.
"""

from __future__ import annotations

from typing import Dict, Optional, Union

import numpy as np
from pandas import Series

from colibri.interfaces.modules.thermal_space import ThermalSpace
from colibri.modules.thermal_spaces.simple_building.simple_building_model import (
    simplified_building_model,
)
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class SimpleBuilding(ThermalSpace):
    def __init__(
        self,
        name: str,
        q_walls: Optional[Dict[str, float]] = None,
        setpoint_temperatures: Optional[Dict[str, float]] = None,
        q_provided: Optional[Dict[str, float]] = None,
        gains: Optional[Dict[str, float]] = None,
        previous_inside_air_temperatures: Optional[Dict[str, float]] = None,
        inside_air_temperatures: Optional[Dict[str, float]] = None,
        q_needs: Optional[Dict[str, float]] = None,
        annual_needs: Optional[Dict[str, float]] = None,
        air_change_rate: float = 0.5,
        area_floor: float = 50.0,
        exterior_air_temperature: float = 10.0,
        exterior_air_temperatures: Optional[Series] = None,
        floor_specific_thermal_conductance: float = 0.25,
        global_area_walls: float = 200.0,
        global_horizontal_radiation: float = 0.0,
        global_horizontal_radiations: Union[float, Series] = 0.0,
        heating_season: Union[bool, Series] = None,
        heat_recovery_efficiency: float = 0.0,
        is_cooling_on: bool = False,
        is_heating_on: bool = True,
        number_of_floors: int = 2,
        roof_specific_thermal_conductance: float = 0.3,
        total_heat_balance: Union[float, np.ndarray] = 0.0,
        wall_specific_thermal_conductance: float = 0.5,
        window_specific_thermal_conductance: float = 2.5,
        window_to_wall_ratio: float = 0.2,
        window_transmission: float = 0.7,
        zone_setpoint_cooling: float = 27.0,
        zone_setpoint_heating: float = 20.0,
        zone_temperature: Union[float, np.ndarray] = 20.0,
    ) -> None:
        """Initialize a new SimpleBuilding instance."""
        if q_walls is None:
            q_walls: Dict[str, float] = dict()
        if setpoint_temperatures is None:
            setpoint_temperatures: Dict[str, float] = dict()
        if q_provided is None:
            q_provided: Dict[str, float] = dict()
        if gains is None:
            gains: Dict[str, float] = dict()
        if previous_inside_air_temperatures is None:
            previous_inside_air_temperatures: Dict[str, float] = dict()
        if inside_air_temperatures is None:
            inside_air_temperatures: Dict[str, float] = dict()
        if q_needs is None:
            q_needs: Dict[str, float] = dict()
        if annual_needs is None:
            annual_needs: Dict[str, float] = dict()
        super().__init__(
            name=name,
            q_walls=q_walls,
            setpoint_temperatures=setpoint_temperatures,
            q_provided=q_provided,
            gains=gains,
            previous_inside_air_temperatures=previous_inside_air_temperatures,
            inside_air_temperatures=inside_air_temperatures,
            q_needs=q_needs,
            annual_needs=annual_needs,
        )
        self.air_change_rate = self.define_parameter(
            name="air_change_rate",
            default_value=air_change_rate,
            description="Ventilation air change rate (ACH).",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.CUBIC_METER_PER_HOUR,
            attached_to=None,
            required=None,
        )
        self.area_floor = self.define_parameter(
            name="area_floor",
            default_value=area_floor,
            description="Total surface area of the floor.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SQUARE_METER,
            attached_to=None,
            required=None,
        )
        self.area_walls = self.define_parameter(
            name="area_walls",
            default_value=None,
            description="Total surface area of the walls.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SQUARE_METER,
            attached_to=None,
            required=None,
        )
        self.area_windows = self.define_parameter(
            name="area_windows",
            default_value=None,
            description="Total surface area of the windows.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SQUARE_METER,
            attached_to=None,
            required=None,
        )
        self.exterior_air_temperatures = self.define_input(
            name="exterior_air_temperatures",
            default_value=exterior_air_temperatures,
            description="Exterior air temperatures.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
        self.exterior_air_temperature = self.define_input(
            name="exterior_air_temperature",
            default_value=exterior_air_temperature,
            description="Exterior air temperature at a given time step.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.floor_specific_thermal_conductance = self.define_parameter(
            name="floor_specific_thermal_conductance",
            default_value=floor_specific_thermal_conductance,
            description="Specific thermal conductance of the floor.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
            attached_to=None,
            required=None,
        )
        self.global_horizontal_radiations = self.define_input(
            name="global_horizontal_radiations",
            default_value=global_horizontal_radiations,
            description="Hourly global horizontal radiation for a year "
            "or at a specific hour "
            "(GloHorzRad in energyPlus weather file format).",
            format=Union[float, Series],
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
        self.global_horizontal_radiation = self.define_input(
            name="global_horizontal_radiation",
            default_value=global_horizontal_radiation,
            description="Hourly global horizontal radiation "
            "at a given time step "
            "(GloHorzRad in energyPlus weather file format).",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=None,
        )
        self.heating_season = self.define_parameter(
            name="heating_season",
            default_value=heating_season,
            description="Heating season.",
            format=Union[bool, Series],
            min=0,
            max=float("inf"),
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.heat_recovery_efficiency = self.define_parameter(
            name="heat_recovery_efficiency",
            default_value=heat_recovery_efficiency,
            description="Heat recovery efficiency for ventilation [%].",
            format=Union[bool, Series],
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.is_cooling_on = self.define_parameter(
            name="is_cooling_on",
            default_value=is_cooling_on,
            description="Specify whether or not the cooling system is on.",
            format=bool,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.is_heating_on = self.define_parameter(
            name="is_heating_on",
            default_value=is_heating_on,
            description="Specify whether or not the heating system is on.",
            format=bool,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.global_area_walls = self.define_parameter(
            name="global_area_walls",
            default_value=global_area_walls,
            description="Total/global area of the walls (without excluding windows).",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SQUARE_METER,
            attached_to=None,
            required=None,
        )
        self.number_of_floors = self.define_parameter(
            name="number_of_floors",
            default_value=number_of_floors,
            description="Number of floors.",
            format=int,
            min=0,
            max=float("inf"),
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.roof_specific_thermal_conductance = self.define_parameter(
            name="roof_specific_thermal_conductance",
            default_value=roof_specific_thermal_conductance,
            description="Specific thermal conductance of the roof.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
            attached_to=None,
            required=None,
        )
        self.total_heat_balance = self.define_parameter(
            name="total_heat_balance",
            default_value=total_heat_balance,
            description="Energy heating or cooling demand of the building.",
            format=Union[float, np.ndarray],
            min=float("-inf"),
            max=float("inf"),
            unit=Units.WATT_HOUR,
            attached_to=None,
            required=None,
        )
        self.volume = self.define_parameter(
            name="volume",
            default_value=None,
            description="Volume of the zone.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.CUBIC_METER,
            attached_to=None,
            required=None,
        )
        self.wall_specific_thermal_conductance = self.define_parameter(
            name="wall_specific_thermal_conductance",
            default_value=wall_specific_thermal_conductance,
            description="Specific thermal conductance of the walls.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
            attached_to=None,
            required=None,
        )
        self.window_specific_thermal_conductance = self.define_parameter(
            name="window_specific_thermal_conductance",
            default_value=window_specific_thermal_conductance,
            description="Specific thermal conductance of the windows.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
            attached_to=None,
            required=None,
        )
        self.window_transmission = self.define_parameter(
            name="window_transmission",
            default_value=window_transmission,
            description="Transmission through windows [%].",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.window_to_wall_ratio = self.define_parameter(
            name="window_to_wall_ratio",
            default_value=window_to_wall_ratio,
            description="Window-to-wall ratio (WWR).",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.zone_setpoint_cooling = self.define_parameter(
            name="zone_setpoint_cooling",
            default_value=zone_setpoint_cooling,
            description="Set point temperature during the cooling season.",
            format=Series,
            min=0,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
            required=None,
        )
        self.zone_setpoint_heating = self.define_parameter(
            name="zone_setpoint_heating",
            default_value=zone_setpoint_heating,
            description="Set point temperature during the heating season.",
            format=float,
            min=0,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
            required=None,
        )
        self.zone_temperature = self.define_output(
            name="zone_temperature",
            default_value=zone_temperature,
            description="Temperature of the zone.",
            format=Union[float, np.ndarray],
            min=0,
            max=float("inf"),
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )

    def initialize(self) -> bool:
        height: float = 2.5
        self.volume = self.area_floor * self.number_of_floors * height
        self.area_windows = self.global_area_walls * self.window_to_wall_ratio
        self.area_walls = self.global_area_walls * (
            1 - self.window_to_wall_ratio
        )
        # Exterior air temperatures and global horizontal radiations come
        # from another module, so as long as they are None,
        # this module is not initialized (return False)
        if (self.exterior_air_temperatures is None) or (
            self.global_horizontal_radiations is None
        ):
            return False
        self.zone_setpoint_temperatures: Series = (
            np.zeros(len(self.exterior_air_temperatures))
            + self.zone_setpoint_heating
        )
        heating_season: Series = np.empty(len(self.exterior_air_temperatures))
        heating_on: Series = (
            self.exterior_air_temperatures.rolling(48).mean() <= 15
        )
        heating_on[0:48] = True
        self.heating_seasons: Series = heating_on
        # Season calculation simple whenever heating is needed
        if self.is_cooling_on:
            self.zone_setpoint_temperatures[heating_season == False] = (
                self.zone_setpoint_cooling
            )
        return True

    def run(self, time_step: int, number_of_iterations: int) -> None:
        heating_season: bool = self.heating_seasons[time_step]
        zone_setpoint_temperature: int = self.zone_setpoint_temperatures[
            time_step
        ]
        self.total_heat_balance, self.zone_temperature = (
            simplified_building_model(
                air_change_rate=self.air_change_rate,
                area_floor=self.area_floor,
                area_walls=self.area_walls,
                area_windows=self.area_windows,
                exterior_air_temperature=self.exterior_air_temperature,
                floor_specific_thermal_conductance=self.floor_specific_thermal_conductance,
                global_horizontal_radiation=self.global_horizontal_radiation,
                heating_season=heating_season,
                heat_recovery_efficiency=self.heat_recovery_efficiency,
                is_cooling_on=self.is_cooling_on,
                is_heating_on=self.is_cooling_on,
                number_of_floors=self.number_of_floors,
                roof_specific_thermal_conductance=self.roof_specific_thermal_conductance,
                volume=self.volume,
                wall_specific_thermal_conductance=self.wall_specific_thermal_conductance,
                window_specific_thermal_conductance=self.window_specific_thermal_conductance,
                window_transmission=self.window_transmission,
                zone_setpoint_temperature=zone_setpoint_temperature,
            )
        )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True


if __name__ == "__main__":
    from pathlib import Path
    from typing import Any

    from colibri.config.constants import LOGGER
    from colibri.core import ProjectOrchestrator
    from colibri.modules import WeatherEpw

    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(
        name="project-1",
        time_steps=20,  # Set time steps
        iterate_for_convergence=False,  # Set no loops (runs twice as fast)
    )
    # Create a weather (from Weather model) and add it to the project orchestrator
    epw_file_path: Path = (
        Path(__file__).resolve().parents[4]
        / "tests"
        / "data"
        / "weather"
        / "epw"
        / "Paris.epw"
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-1", epw_file_path=epw_file_path
    )
    project_orchestrator.add_module(module=weather)
    # Create a building (from SimpleBuilding model) and add it to the project orchestrator
    building: SimpleBuilding = SimpleBuilding(
        "building-1",
        is_cooling_on=False,
        is_heating_on=True,
    )
    project_orchestrator.add_module(module=building)
    # Link temperature and radiation from weather to building (for post-initialization)
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperatures",
        building,
        "exterior_air_temperatures",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiations",
        building,
        "global_horizontal_radiations",
    )
    # Link temperature and radiation from weather to building
    project_orchestrator.add_link(
        weather,
        "exterior_air_temperature",
        building,
        "exterior_air_temperature",
    )
    project_orchestrator.add_link(
        weather,
        "global_horizontal_radiation",
        building,
        "global_horizontal_radiation",
    )
    # Run project
    run_information: Dict[str, Any] = project_orchestrator.run()
    LOGGER.info(run_information)
    zone_temperature_series = building.zone_temperature_series
    LOGGER.info(zone_temperature_series)
