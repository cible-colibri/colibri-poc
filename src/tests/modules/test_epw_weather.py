"""
Tests for the `epw_weather.py` module.
"""

from pathlib import Path
from typing import List

import pytest
from pandas import Series

from colibri.interfaces import Weather
from colibri.modules import WeatherEpw


def test_weather_model() -> None:
    """Test the WeatherEpw class."""
    epw_file_path: Path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "weather"
        / "epw"
        / "Paris.epw"
    )
    weather: WeatherEpw = WeatherEpw(
        name="weather-1",
        exterior_air_temperature=17,
        epw_file_path=epw_file_path,
    )
    assert isinstance(weather, WeatherEpw) is True
    assert isinstance(weather, Weather) is True
    assert weather.exterior_air_temperature == 17
    weather.initialize()
    expected_exterior_air_temperatures: List[float] = [2.9, 4.3, 5.3]
    expected_ground_temperatures: List[float] = [6.277, 6.276, 6.274]
    for time_step in range(0, 3):
        weather.run(time_step=time_step, number_of_iterations=1)
        assert (
            weather.exterior_air_temperature
            == expected_exterior_air_temperatures[time_step]
        )
        assert weather.ground_temperatures[time_step] == pytest.approx(
            expected_ground_temperatures[time_step], abs=0.001
        )
    weather_2: WeatherEpw = WeatherEpw(
        name="weather-1",
        exterior_air_temperature=17,
        epw_file_path=epw_file_path,
        constant_ground_temperature=18,
    )
    weather_2.initialize()
    expected_ground_temperatures: List[float] = [6.277, 6.276, 6.274]
    for time_step in range(0, 3):
        weather_2.run(time_step=time_step, number_of_iterations=1)
        assert (
            weather_2.exterior_air_temperature
            == expected_exterior_air_temperatures[time_step]
        )
        assert weather.ground_temperatures[time_step] == pytest.approx(
            expected_ground_temperatures[time_step], abs=0.001
        )
    shorter_exterior_air_temperatures: Series = (
        weather_2.exterior_air_temperatures.loc[:3]
    )
    assert weather.ground_temperatures_kusuda(
        exterior_air_temperatures=weather.exterior_air_temperatures.loc[:4000],
        ground_diffusivity=0.645e-6 * 3600.0,
        depth=0.25,
    ).mean() == pytest.approx(7.5, abs=0.2)


if __name__ == "__main__":
    test_weather_model()
