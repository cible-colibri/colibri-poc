"""
WeatherEpw class from Weather interface.
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
from numpy import ndarray
from pandas import Series

from colibri.interfaces.modules.weather import Weather
from colibri.utils.enums_utils import Roles, Units


class WeatherEpw(Weather):
    def __init__(
        self,
        name: str,
        epw_file_path: Union[Path, str],
        exterior_air_temperature: float = 0.0,
        constant_ground_temperature: Optional[float] = None,
        ground_temperatures: Optional[Series] = None,
        sky_temperatures: Optional[Series] = None,
        rolling_time_window: int = 48,
        rolling_exterior_air_temperatures: Optional[Series] = None,
        exterior_air_temperatures: Optional[Series] = None,
        solar_direct: Optional[Series] = None,
        solar_diffuse: Optional[Series] = None,
        global_horizontal_radiation: Optional[Series] = None,
    ):
        super().__init__(
            name=name, exterior_air_temperature=exterior_air_temperature
        )
        self.epw_file_path: Union[Path, str] = self.define_parameter(
            name="epw_file_path",
            default_value=epw_file_path,
            description="Path to the EPW file.",
            format=Union[Path, str],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
        )
        self.constant_ground_temperature: float = self.define_parameter(
            name="constant_ground_temperature",
            default_value=constant_ground_temperature,
            description="Constant temperature of the ground.",
            format=float,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.ground_temperatures: Series = self.define_output(
            name="ground_temperatures",
            default_value=ground_temperatures,
            description="Temperatures of the ground.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.sky_temperatures: Series = self.define_output(
            name="sky_temperatures",
            default_value=sky_temperatures,
            description="Temperatures of the sky.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.rolling_time_window: int = self.define_output(
            name="rolling_time_window",
            default_value=rolling_time_window,
            description="Rolling time window to compute the rolling exterior air temperatures.",
            format=int,
            min=24,
            max=48,
            unit=Units.UNITLESS,
            attached_to=None,
        )
        self.rolling_exterior_air_temperatures: Series = self.define_output(
            name="rolling_exterior_air_temperatures",
            default_value=rolling_exterior_air_temperatures,
            description="Exterior rolling air temperatures.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.exterior_air_temperatures: Series = self.define_output(
            name="exterior_air_temperatures",
            default_value=exterior_air_temperatures,
            description="Exterior air temperatures.",
            format=Series,
            min=-100,
            max=100,
            unit=Units.DEGREE_CELSIUS,
            attached_to=None,
        )
        self.latitude: float = self.define_output(
            name="latitude",
            default_value=48,
            description="Latitude of the location.",
            format=float,
            min=-90,
            max=90,
            unit=Units.DEGREE,
            attached_to=None,
        )
        self.longitude: float = self.define_output(
            name="longitude",
            default_value=2,
            description="Longitude of the location.",
            format=float,
            min=-180,
            max=180,
            unit=Units.DEGREE,
            attached_to=None,
        )
        self.solar_diffuse: Series = self.define_output(
            name="solar_direct",
            default_value=solar_direct,
            description="Direct solar radiation.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=None,
        )
        self.solar_diffuse = self.define_output(
            name="solar_diffuse",
            default_value=solar_diffuse,
            description="Diffuse solar radiation.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=None,
        )
        self.global_horizontal_radiation = self.define_output(
            name="global_horizontal_radiation",
            default_value=0.0,
            description="Global horizontal radiation.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=None,
        )
        self.global_horizontal_radiations = self.define_output(
            name="global_horizontal_radiations",
            default_value=global_horizontal_radiation,
            description="Global horizontal radiation.",
            format=Series,
            min=0,
            max=float("inf"),
            unit=Units.WATT_PER_SQUARE_METER,
            attached_to=None,
        )
        self._weather_data: Optional[Series] = None

    def initialize(self) -> None:
        self.read_epw_file()
        # Compute ground temperatures
        if self.constant_ground_temperature is not None:
            self.ground_temperatures = (
                self.constant_ground_temperature
                * np.ones(self._weather_data["ground_temperature"].shape)
            )
        else:
            self.ground_temperatures = self._weather_data["ground_temperature"]
        # Compute sky temperatures
        self.sky_temperatures = self._weather_data["sky_temperature"]
        # Compute rolling_exterior_air_temperatures
        self.rolling_exterior_air_temperatures = (
            self.exterior_air_temperatures.rolling(
                self.rolling_time_window
            ).mean()
        )
        self.rolling_exterior_air_temperatures[0 : self.rolling_time_window] = (
            self.rolling_exterior_air_temperatures[
                self.rolling_time_window : 2 * self.rolling_time_window
            ]
        )
        self.global_horizontal_radiations = self._weather_data["GloHorzRad"]

    def post_initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        self.exterior_air_temperature = self.exterior_air_temperatures[
            time_step
        ]
        self.global_horizontal_radiation = self.global_horizontal_radiations[
            time_step
        ]

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True

    def read_epw_file(self) -> None:
        epw_columns: Tuple = (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "datasource",
            "temperature",
            "DewPoint",
            "RelHum",
            "pressure",
            "ExtHorzRad",
            "ExtDirRad",
            "HorzIRSky",
            "GloHorzRad",
            "direct_radiation",
            "diffuse_radiation",
            "GloHorzIllum",
            "DirNormIllum",
            "DifHorzIllum",
            "ZenLum",
            "wind_direction",
            "wind_speed",
            "TotSkyCvr",
            "OpaqSkyCvr",
            "Visibility",
            "Ceiling",
            "presweathobs",
            "presweathcodes",
            "precipwtr",
            "aerosoloptdepth",
            "snowdepth",
            "dayslastsnow",
            "albedo",
            "rain",
            "rain_hr",
        )
        self._weather_data = pd.read_csv(
            Path(self.epw_file_path), skiprows=8, header=None, names=epw_columns
        )
        self.latitude, self.longitude = tuple(
            pd.read_csv(Path(self.epw_file_path), header=None, nrows=1)
            .loc[:, 6:7]
            .values.flatten()
            .tolist()
        )
        self.solar_direct = self._weather_data["direct_radiation"]
        self.solar_diffuse = self._weather_data["diffuse_radiation"]
        self.exterior_air_temperatures = self._weather_data.temperature
        # Compute sky temperature
        dew_temperature: Series = self._weather_data["DewPoint"]
        opaque_sky_cover: Series = self._weather_data["OpaqSkyCvr"]
        sigma: float = 5.66797e-8
        reduced_opaque_sky_cover: Series = opaque_sky_cover / 10.0
        sky_emissivity: Series = (
            0.787 + 0.764 * np.log((dew_temperature + 273.15) / 273.15)
        ) * (
            1
            + 0.0224 * reduced_opaque_sky_cover
            - 0.0035 * reduced_opaque_sky_cover**2
            + 0.00028 * reduced_opaque_sky_cover**3
        )
        horizontal_ir: Series = (
            sky_emissivity
            * sigma
            * (self._weather_data["temperature"] + 273.15) ** 4
        )
        sky_temperature: Series = (horizontal_ir / sigma) ** 0.25 - 273.15
        self._weather_data["sky_temperature"] = np.array(sky_temperature.values)
        self._weather_data["opaque_sky_cover"] = np.array(
            opaque_sky_cover.values
        )
        # Compute ground temperature
        depth: float = 0.25
        ground_diffusivity: float = 0.645e-6 * 3600.0
        self._weather_data["ground_temperature"] = (
            self.ground_temperatures_kusuda(
                exterior_air_temperatures=self._weather_data["temperature"],
                ground_diffusivity=ground_diffusivity,
                depth=depth,
            )
        )

    @staticmethod
    def ground_temperatures_kusuda(
        exterior_air_temperatures: Series,
        ground_diffusivity: float,
        depth: float,
    ) -> Series:
        if len(exterior_air_temperatures) != 8760:
            time_window: int = 168 * 4
            ground_temperatures: Series = exterior_air_temperatures.rolling(
                time_window
            ).mean()
            ground_temperatures[0:time_window] = ground_temperatures[
                time_window : 2 * time_window
            ]
        else:
            rolling_exterior_air_temperatures: Series = (
                exterior_air_temperatures.rolling(int(24.0 * 30.5))
                .mean()
                .bfill()
            )
            ground_temperature_difference: float = (
                max(rolling_exterior_air_temperatures)
                - min(rolling_exterior_air_temperatures)
            ) / 2.0
            ground_mean_temperature: float = np.mean(
                rolling_exterior_air_temperatures
            )
            time: ndarray = (
                np.array(list(range(len(exterior_air_temperatures)))) + 1.0
            ) / 24.0
            phase_shift: int = int(exterior_air_temperatures.idxmin() / 24)
            # Kusuda equation 1965
            ground_temperatures = (
                ground_mean_temperature
                - ground_temperature_difference
                * np.exp(-depth * np.sqrt(np.pi / (ground_diffusivity * 365.0)))
                * np.cos(
                    2
                    * np.pi
                    / 365.0
                    * (
                        time
                        - phase_shift
                        - depth
                        / 2.0
                        * np.sqrt(365.0 / (np.pi * ground_diffusivity))
                    )
                )
            )

        return ground_temperatures


if __name__ == "__main__":
    epw_file_path: Path = (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "data"
        / "weather"
        / "epw"
        / "Paris.epw"
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-epw",
        epw_file_path=epw_file_path,
    )
    weather.initialize()
    weather.run(2, 1)
    print(weather.exterior_air_temperature)
    weather.run(3, 1)
    print(weather.exterior_air_temperature)
    print(
        weather.ground_temperatures_kusuda(
            exterior_air_temperatures=weather.exterior_air_temperatures.loc[
                :4000
            ],
            ground_diffusivity=0.645e-6 * 3600.0,
            depth=0.25,
        )
    )
