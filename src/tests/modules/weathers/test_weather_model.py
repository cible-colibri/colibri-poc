"""
Tests for the `weather_model.py` module.
"""

from typing import List

from colibri.interfaces import Weather
from colibri.modules import WeatherModel


def test_weather_model() -> None:
    """Test the WeatherModel class."""
    weather: WeatherModel = WeatherModel(
        name="weather-1", exterior_air_temperature=17
    )
    assert isinstance(weather, WeatherModel) is True
    assert isinstance(weather, Weather) is True
    assert weather.exterior_air_temperature == 17
    weather.altitudes = [100, 200, 300]
    weather.scenario_exterior_air_temperatures = [20, 30, 40, 50]
    weather.initialize()
    corrected_temperatures: List[float] = [18.7, 28.7, 38.7, 48.7]
    assert weather.corrected_exterior_air_temperatures == corrected_temperatures
    for time_step in range(0, 3):
        weather.run(time_step=time_step, number_of_iterations=1)
        assert (
            weather.exterior_air_temperature
            == corrected_temperatures[time_step]
        )
        assert (
            weather.has_converged(time_step=time_step, number_of_iterations=1)
            is True
        )


if __name__ == "__main__":
    test_weather_model()
