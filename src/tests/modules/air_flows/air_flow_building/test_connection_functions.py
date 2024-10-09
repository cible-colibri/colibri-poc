"""
Tests for the `connection_functions.py` module.
"""

import pytest

from colibri.modules.air_flows.air_flow_building.connection_functions import (
    compute_door_back_pressure_coefficient,
    compute_dtu_duct_pressure_loss,
    compute_grille_back_pressure_coefficient,
    compute_pressure_loss_for_mechanical_fans,
)


def test_compute_door_back_pressure_coefficient() -> None:
    """Test the compute_door_back_pressure_coefficient function."""
    assert compute_door_back_pressure_coefficient() == pytest.approx(
        1.70, abs=0.025
    )
    assert compute_door_back_pressure_coefficient(
        section=2.5, discharge_coefficient=0.65, opening=0.25
    ) == pytest.approx(0.57, abs=0.025)


def test_compute_dtu_duct_pressure_loss() -> None:
    """Test the compute_dtu_duct_pressure_loss function."""
    assert compute_dtu_duct_pressure_loss() == pytest.approx(1.27, abs=0.025)
    assert compute_dtu_duct_pressure_loss(
        flow_rate=55.0,
        density=1.2,
        section=0.005,
        hydraulic_diameter=0.08,
        length=2.5,
        friction_factor=3.0e6,
        pressure_drop_coefficients=[0.0, 0.0],
        computation_mode="pressure",
    ) == pytest.approx(4.63, abs=0.025)
    assert compute_dtu_duct_pressure_loss(
        flow_rate=55.0,
        density=1.2,
        section=0.005,
        hydraulic_diameter=0.08,
        length=2.5,
        friction_factor=3.0e6,
        pressure_drop_coefficients=[0.0, 0.0],
        computation_mode="c_lin",
    ) == pytest.approx(436.9, abs=0.025)
    with pytest.raises(Exception) as exception_information:
        _ = compute_dtu_duct_pressure_loss(
            flow_rate=55.0,
            density=1.2,
            section=0.005,
            hydraulic_diameter=0.08,
            length=2.5,
            friction_factor=3.0e6,
            pressure_drop_coefficients=[0.0, 0.0],
            computation_mode="wrong_computation_mode",
        )
    assert exception_information.typename == ValueError.__name__
    assert (
        str(exception_information.value)
        == "Unknown 'wrong_computation_mode' computation mode for the duct model."
    )


def test_compute_grille_back_pressure_coefficient() -> None:
    """Test the compute_grille_back_pressure_coefficient function."""
    assert compute_grille_back_pressure_coefficient() == pytest.approx(
        3.4e-05, abs=1e-06
    )
    assert compute_grille_back_pressure_coefficient(
        dp_0=40.0,
        rho_0=1.2,
        flow_0=1.5,
        n=0.5,
        opening=0.4,
    ) == pytest.approx(2.8e-05, abs=1e-06)


def test_compute_pressure_loss_for_mechanical_fans() -> None:
    """Test the compute_pressure_loss_for_mechanical_fans function."""

    assert compute_pressure_loss_for_mechanical_fans() == pytest.approx(
        -80.0, abs=0.5
    )
    assert compute_pressure_loss_for_mechanical_fans(
        flow_rate=63, delta_pressure_law=[[0, 50, 110], [85, 85, 0]]
    ) == pytest.approx(-66.5, abs=0.5)


if __name__ == "__main__":
    test_compute_door_back_pressure_coefficient()
    test_compute_dtu_duct_pressure_loss()
    test_compute_grille_back_pressure_coefficient()
    test_compute_pressure_loss_for_mechanical_fans()
