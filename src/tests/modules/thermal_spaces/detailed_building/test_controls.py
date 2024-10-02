"""
Tests for the `controls.py` module.
"""

import math
from typing import List, Tuple

import numpy as np
import pytest
from numpy import ndarray

from colibri.modules.thermal_spaces.detailed_building.controls import (
    compute_ventilation_losses,
    get_operation_mode,
    space_temperature_control_simple,
)


def test_compute_ventilation_losses() -> None:
    """Test the compute_ventilation_losses function."""
    ventilation_losses: ndarray = compute_ventilation_losses(
        flows=[
            ["BC0", "living_room_1", 0.134],
            ["living_room_1", "kitchen_1", 0.134],
        ],
        air_temperatures={"living_room_1": 22.5, "kitchen_1": 21.0},
        outdoor_temperature=13.0,
        efficiency_heat_recovery=0.0,
    )
    expected_ventilation_losses: List[float] = [-0.42, 0.07]
    assert isinstance(ventilation_losses, ndarray) is True
    for index, ventilation_loss in enumerate(ventilation_losses):
        assert ventilation_loss == pytest.approx(
            expected_ventilation_losses[index], abs=0.025
        )


def test_get_operation_mode() -> None:
    """Test the get_operation_mode function."""
    operation_mode: Tuple[List[str], ndarray] = get_operation_mode(
        indoor_temperatures=np.array([20.0, 20.0]),
        outdoor_temperature=5.0,
        heating_setpoints=np.array([0.0, 0.0]),
        cooling_setpoints=np.array([0.0, 0.0]),
        operating_modes=["cooling", "heating"],
    )
    assert isinstance(operation_mode, tuple) is True
    assert isinstance(operation_mode[0], list) is True
    assert isinstance(operation_mode[1], ndarray) is True
    assert operation_mode[0][0] == "free_float"
    assert operation_mode[0][1] == "free_float"
    assert math.isnan(operation_mode[1][0]) is True
    assert math.isnan(operation_mode[1][1]) is True

    operation_mode: Tuple[List[str], ndarray] = get_operation_mode(
        indoor_temperatures=np.array([18.5, 17.0]),
        outdoor_temperature=5.0,
        heating_setpoints=np.array([19.0, 21.0]),
        cooling_setpoints=np.array([26.0, 24.0]),
        operating_modes=["cooling", "heating"],
    )
    assert isinstance(operation_mode, tuple) is True
    assert isinstance(operation_mode[0], list) is True
    assert isinstance(operation_mode[1], ndarray) is True
    assert operation_mode[0][0] == "heating"
    assert operation_mode[0][1] == "heating"
    assert operation_mode[1][0] == pytest.approx(19.0, abs=0.25)
    assert operation_mode[1][1] == pytest.approx(21.0, abs=0.25)

    operation_mode: Tuple[List[str], ndarray] = get_operation_mode(
        indoor_temperatures=np.array([16.0, 27.0]),
        outdoor_temperature=30.0,
        heating_setpoints=np.array([19.0, 21.0]),
        cooling_setpoints=np.array([26.0, 24.0]),
        operating_modes=["cooling", "heating"],
    )
    assert isinstance(operation_mode, tuple) is True
    assert isinstance(operation_mode[0], list) is True
    assert isinstance(operation_mode[1], ndarray) is True
    assert operation_mode[0][0] == "free_float"
    assert operation_mode[0][1] == "cooling"
    assert math.isnan(operation_mode[1][0]) is True
    assert operation_mode[1][1] == pytest.approx(24.0, abs=0.25)

    operation_mode: Tuple[List[str], ndarray] = get_operation_mode(
        indoor_temperatures=np.array([16.0, 16.0]),
        outdoor_temperature=14.0,
        heating_setpoints=np.array([20.0, 20.0]),
        cooling_setpoints=np.array([20.0, 20.0]),
        operating_modes=["cooling", "cooling"],
    )
    assert isinstance(operation_mode, tuple) is True
    assert isinstance(operation_mode[0], list) is True
    assert isinstance(operation_mode[1], ndarray) is True
    assert operation_mode[0][0] == "free_float"
    assert operation_mode[0][1] == "free_float"
    assert math.isnan(operation_mode[1][0]) is True
    assert math.isnan(operation_mode[1][1]) is True

    operation_mode: Tuple[List[str], ndarray] = get_operation_mode(
        indoor_temperatures=np.array([16.0, 16.0]),
        outdoor_temperature=17.0,
        heating_setpoints=np.array([20.0, 20.0]),
        cooling_setpoints=np.array([20.0, 20.0]),
        operating_modes=["heating", "heating"],
    )
    assert isinstance(operation_mode, tuple) is True
    assert isinstance(operation_mode[0], list) is True
    assert isinstance(operation_mode[1], ndarray) is True
    assert operation_mode[0][0] == "free_float"
    assert operation_mode[0][1] == "free_float"
    assert math.isnan(operation_mode[1][0]) is True
    assert math.isnan(operation_mode[1][1]) is True


def test_space_temperature_control_simple() -> None:
    """Test the space_temperature_control_simple function."""
    x = space_temperature_control_simple(
        operating_modes=["free_float", "free_float"],
        temperature_setpoints=np.array([np.nan, np.nan]),
        system_matrix=np.array(
            [
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 1.1],
                [9.9, 4.2, 4.6, 9.9, 4.2, 4.6, 9.9, 4.2, 4.6, 9.9, 4.2, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.0, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 1.1],
            ]
        ),
        control_matrix=np.array(
            [
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
                [9.9, 4.2, 4.6, 9.9, 4.2, 4.6, 9.9, 4.2, 4.6, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
                [1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1, 4.9, 5.5, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
                [4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 4.9, 2.1, 2.3, 1.1],
            ]
        ),
        states_last=np.array(
            [
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
                20.0,
            ]
        ),
        input_signals=np.array(
            [10.0, 10.0, 2.9, 2.9, 2.9, 2.9, -4.26, -4.26, -4.26]
        ),
        index_states={
            "boundaries": {"start_index": 0, "n_elements": 8},
            "windows": {"start_index": 6, "n_elements": 2},
            "spaces_mean_radiant": {"start_index": 8, "n_elements": 2},
            "spaces_air": {"start_index": 10, "n_elements": 2},
        },
        index_inputs={
            "ground_temperature": {"start_index": 0, "n_elements": 1},
            "exterior_air_temperature": {"start_index": 1, "n_elements": 4},
            "exterior_radiant_temperature": {
                "start_index": 13,
                "n_elements": 12,
            },
            "radiative_gain_boundary_external": {
                "start_index": 25,
                "n_elements": 12,
            },
            "space_radiative_gain": {"start_index": 37, "n_elements": 2},
            "space_convective_gain": {"start_index": 39, "n_elements": 2},
        },
        radiative_share_hvac=np.array([0.0, 0.0]),
        max_heating_power=np.array([10_000, 10_000]),
        max_cooling_power=np.array([10_000, 10_000]),
        ventilation_gain_coefficients=np.array([63327.7, 28845.9]),
        efficiency_heat_recovery=0.0,
        convective_internal_gains=np.array([80.0, 80.0]),
        radiative_internal_gains=np.array([120.0, 120.0]),
        internal_temperatures={"living_room_1": 20.0, "kitchen_1": 20.0},
        flows=np.array([]),
    )
    print(x)


if __name__ == "__main__":
    test_compute_ventilation_losses()
    test_get_operation_mode()
    test_space_temperature_control_simple()
