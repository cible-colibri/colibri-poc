"""
Tests for the `connection_functions.py` module.
"""

import pytest

from colibri.modules.air_flows.air_flow_building.connection_functions import (
    compute_pressure_loss_for_mechanical_fans,
)


def test_compute_pressure_loss_for_mechanical_fans() -> None:
    """Test the compute_pressure_loss_for_mechanical_fans function."""

    assert compute_pressure_loss_for_mechanical_fans() == pytest.approx(
        -80.0, abs=0.5
    )
    assert compute_pressure_loss_for_mechanical_fans(
        flow_rate=63, delta_pressure_law=[[0, 50, 110], [85, 85, 0]]
    ) == pytest.approx(-66.5, abs=0.5)


if __name__ == "__main__":
    test_compute_pressure_loss_for_mechanical_fans()
