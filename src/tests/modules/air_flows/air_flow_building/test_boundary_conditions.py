"""
Tests for the `boundary_conditions.py` module.
"""

from typing import Dict, List, Tuple

import numpy as np
import pytest
from pandas import Series

from colibri.modules.air_flows.air_flow_building.boundary_conditions import (
    compute_boundary_conditions,
)
from colibri.project_objects import BoundaryCondition


def test_compute_boundary_conditions() -> None:
    """Test the compute_boundary_conditions function."""
    exterior_air_temperatures: Series = Series(data=[20.0, 19.5, 19.0, 21.0])
    number_of_time_steps: int = 4
    dynamic_test: int = 1
    apply_disturbance: Tuple[int, int] = [24, 0]
    boundary_conditions: List[BoundaryCondition] = [
        BoundaryCondition(
            id="boundary-condition-1", label="boundary-condition-1"
        ),
        BoundaryCondition(
            id="boundary-condition-2", label="boundary-condition-2"
        ),
    ]
    assert (
        compute_boundary_conditions(
            exterior_air_temperatures=exterior_air_temperatures,
            boundary_conditions=boundary_conditions,
            number_of_time_steps=number_of_time_steps,
            dynamic_test=dynamic_test,
            apply_disturbance=apply_disturbance,
        )
        is None
    )
    expected_exterior_air_temperatures: Dict[str, np.ndarray] = {
        "boundary-condition-1": np.array([20.0, 19.5, 19.0, 21.0]),
        "boundary-condition-2": np.array([20.0, 19.5, 19.0, 21.0]),
    }
    expected_pressures: Dict[str, np.ndarray] = {
        "boundary-condition-1": np.array([-30.0, -30.0, -30.1, -30.2]),
        "boundary-condition-2": np.array([-30.0, -30.1, -30.3, -30.6]),
    }
    for boundary_condition in boundary_conditions:
        for index, exterior_air_temperature in enumerate(
            boundary_condition.exterior_air_temperatures
        ):
            assert exterior_air_temperature == pytest.approx(
                expected_exterior_air_temperatures[boundary_condition.id][
                    index
                ],
                abs=0.5,
            )
        for index, pressure in enumerate(boundary_condition.pressures):
            assert pressure == pytest.approx(
                expected_pressures[boundary_condition.id][index], abs=0.5
            )
    apply_disturbance = [24, 1]
    assert (
        compute_boundary_conditions(
            exterior_air_temperatures=exterior_air_temperatures,
            boundary_conditions=boundary_conditions,
            number_of_time_steps=number_of_time_steps,
            dynamic_test=dynamic_test,
            apply_disturbance=apply_disturbance,
        )
        is None
    )
    expected_pressures: Dict[str, np.ndarray] = {
        "boundary-condition-1": np.array([-30.0, -6.0, -6.1, -6.2]),
        "boundary-condition-2": np.array([-30.0, 17.9, 17.7, 17.4]),
    }
    for boundary_condition in boundary_conditions:
        for index, exterior_air_temperature in enumerate(
            boundary_condition.exterior_air_temperatures
        ):
            assert exterior_air_temperature == pytest.approx(
                expected_exterior_air_temperatures[boundary_condition.id][
                    index
                ],
                abs=0.5,
            )
        for index, pressure in enumerate(boundary_condition.pressures):
            assert pressure == pytest.approx(
                expected_pressures[boundary_condition.id][index], abs=0.5
            )


if __name__ == "__main__":
    test_compute_boundary_conditions()
