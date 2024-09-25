"""
Tests for the `simplified_building_model.py` module.
"""

from typing import List

import pytest
from pandas import Series

from colibri.modules.thermal_spaces.simple_building.simple_building_model import (
    simplified_building_model,
)


def test_simplified_building_model() -> None:
    """Test the simplified_building_model function."""
    exterior_air_temperatures: Series = Series(data=[20.0, 19.5, 19.0, 21.0])
    global_horizontal_radiations: Series = Series(
        data=[200.0, 200.0, 200.0, 250.0]
    )
    heating_seasons: Series = Series(data=[False, False, False, False])
    zone_setpoint_temperatures: Series = Series(data=[19.0, 19.0, 19.0, 19.0])
    total_heat_balances, zone_temperatures = simplified_building_model(
        air_change_rate=0.5,
        area_floor=50.0,
        area_walls=150.0,
        area_windows=50.0,
        exterior_air_temperature=exterior_air_temperatures,
        floor_specific_thermal_conductance=0.25,
        global_horizontal_radiation=global_horizontal_radiations,
        heating_season=heating_seasons,
        heat_recovery_efficiency=0.0,
        is_cooling_on=True,
        is_heating_on=False,
        number_of_floors=2,
        roof_specific_thermal_conductance=0.3,
        volume=250.0,
        wall_specific_thermal_conductance=0.5,
        window_specific_thermal_conductance=2.5,
        window_transmission=0.7,
        zone_setpoint_temperature=zone_setpoint_temperatures,
    )
    expected_total_heat_balances: List[float] = [
        -3017.8,
        -2889.4,
        -2760.9,
        -3594.5,
    ]
    for index, total_heat_balance in enumerate(total_heat_balances):
        assert total_heat_balance == pytest.approx(
            expected_total_heat_balances[index],
            abs=0.5,
        )
    expected_zone_temperatures: List[float] = [20.0, 20.0, 20.0, 20.0]
    for index, zone_temperature in enumerate(zone_temperatures):
        assert zone_temperature == pytest.approx(
            expected_zone_temperatures[index],
            abs=0.5,
        )

    total_heat_balance, zone_temperature = simplified_building_model(
        air_change_rate=0.5,
        area_floor=50.0,
        area_walls=150.0,
        area_windows=50.0,
        exterior_air_temperature=18.0,
        floor_specific_thermal_conductance=0.25,
        global_horizontal_radiation=200.0,
        heating_season=False,
        heat_recovery_efficiency=0.0,
        is_cooling_on=True,
        is_heating_on=False,
        number_of_floors=2,
        roof_specific_thermal_conductance=0.3,
        volume=250.0,
        wall_specific_thermal_conductance=0.5,
        window_specific_thermal_conductance=2.5,
        window_transmission=0.7,
        zone_setpoint_temperature=20.0,
    )
    assert total_heat_balance == pytest.approx(
        -2211.2,
        abs=0.5,
    )
    assert zone_temperature == pytest.approx(
        20.0,
        abs=0.5,
    )


if __name__ == "__main__":
    test_simplified_building_model()
