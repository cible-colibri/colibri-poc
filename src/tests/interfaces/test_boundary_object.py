"""
Tests for the `boundary.py` module.
"""

from typing import List

import pytest

from colibri.interfaces import ElementObject
from colibri.project_objects import Boundary


def compute_from_layers_properties(layers: List["Layer"]) -> float:
    """Computer the boundary's properties from its layers

    Parameters
    ----------
    layers : List["Layer"]
        List of layers

    Returns
    -------
    u_value: float
        Total U of the layers

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    resistance: float = 0.0
    for layer in layers:
        resistance += layer.thickness / layer.thermal_conductivity
    u_value: float = 0.0
    if resistance > 0:
        u_value = 1.0 / resistance
    return u_value


def test_boundary() -> None:
    """Test the Boundary class"""
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-1",
            "label": "concrete",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.2,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "name": "layer-2",
            "label": "concrete",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.4,
        },
    )
    boundary_1: Boundary = Boundary(
        id="boundary-1",
        label="kitchen-living-room",
        side_1="kitchen",
        side_2="living-room",
        area=4,
        azimuth=90,
        tilt=90,
        layers=[layer_1],
        spaces=[],
    )
    boundary_2: Boundary = Boundary(
        id="boundary-2",
        label="kitchen-restroom",
        side_1="kitchen",
        side_2="restroom",
        area=2.5,
        azimuth=90,
        tilt=90,
        layers=[layer_1, layer_2],
        spaces=[],
        u_value=0.8,
    )
    assert isinstance(boundary_1, Boundary) is True
    assert hasattr(boundary_1, "u_value") is False
    assert compute_from_layers_properties(boundary_1.layers) == pytest.approx(
        2.5, abs=0.1
    )
    assert boundary_2.u_value == pytest.approx(0.8, abs=0.1)
    assert compute_from_layers_properties(boundary_2.layers) == pytest.approx(
        0.83, abs=0.1
    )


if __name__ == "__main__":
    test_boundary()
