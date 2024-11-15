"""
WeatherModel class from Weather interface.
"""

from typing import List

from colibri.interfaces.modules.weather import Weather
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class WeatherModel(Weather):
    def __init__(
        self,
        name: str,
        exterior_air_temperature: float = 0.0,
        altitudes: List[float] = [0.0],
        scenario_exterior_air_temperatures: List[float] = [],
    ):
        super().__init__(
            name=name, exterior_air_temperature=exterior_air_temperature
        )
        self.altitudes = self.define_parameter(
            name="altitudes",
            default_value=altitudes,
            description="Altitudes.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.METER,
        )
        self.scenario_exterior_air_temperatures = self.define_parameter(
            name="scenario_exterior_air_temperatures",
            default_value=scenario_exterior_air_temperatures,
            description="Exterior air temperatures.",
            format=float,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
        )
        self.corrected_exterior_air_temperatures = self.define_parameter(
            name="corrected_exterior_air_temperatures",
            default_value=list(),
            description="Exterior air temperature "
            "corrected with mean altitude.",
            format=List[float],
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
                from_archetype=True,
            ),
        )
        self.temperature_diminution_with_altitude: float = 0.0065  # °C/m

    def initialize(self) -> bool:
        mean_altitude = sum(self.altitudes) / len(self.altitudes)
        self.corrected_exterior_air_temperatures: List[float] = [
            temperature
            - self.temperature_diminution_with_altitude * mean_altitude
            for temperature in self.scenario_exterior_air_temperatures
        ]

    def run(self, time_step: int, number_of_iterations: int) -> None:
        self.exterior_air_temperature = (
            self.corrected_exterior_air_temperatures[time_step]
        )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True
