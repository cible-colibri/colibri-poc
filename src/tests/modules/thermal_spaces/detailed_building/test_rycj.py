"""
Tests for the `rycj.py` module.
"""

from typing import Dict, List

import numpy as np
import pytest
from numpy import ndarray

from colibri.interfaces import BoundaryObject, ElementObject
from colibri.modules.thermal_spaces.detailed_building.rycj import (
    generate_euler_exponential_system_and_control_matrices,
    generate_system_and_control_matrices,
    get_states_from_index,
    get_window_u_value,
    run_state_space,
    set_boundary_discretization_properties,
    set_input_signals_from_index,
    set_radiative_shares,
    set_u_values,
)
from colibri.project_objects import Boundary, Space


def test_generate_euler_exponential_system_and_control_matrices() -> None:
    """Test generate_euler_exponential_system_and_control_matrices function."""
    # Test no. 1
    system_matrix: ndarray = np.array([[0, 1], [-1, 0]])
    control_matrix: ndarray = np.array([[0], [1]])
    time_step: int = 1
    system_matrix_exponential, control_matrix_exponential = (
        generate_euler_exponential_system_and_control_matrices(
            system_matrix=system_matrix,
            control_matrix=control_matrix,
            time_step=time_step,
        )
    )
    assert isinstance(system_matrix_exponential, ndarray) is True
    assert isinstance(control_matrix_exponential, ndarray) is True
    np.testing.assert_array_almost_equal(
        system_matrix_exponential,
        np.array([[0.540, 0.841], [0.000, 0.540]]),
        decimal=3,
    )
    # Test no. 2
    invalid_matrix = np.array([[0, 1, 2], [1, 0, 2]])
    with pytest.raises(ValueError) as exception_information:
        generate_euler_exponential_system_and_control_matrices(
            invalid_matrix, control_matrix, time_step
        )
        assert isinstance(system_matrix_exponential, ndarray) is True
        assert isinstance(control_matrix_exponential, ndarray) is True
    assert exception_information.typename == ValueError.__name__
    assert "exponential A matrix cannot be computed" in str(
        exception_information.value
    )
    # Test no. 3
    invalid_matrix: ndarray = np.array([[1, 2], [1, 2]])
    control_matrix = np.array([[1], [0]])
    time_step: int = 1
    with pytest.raises(Exception) as exception_information:
        generate_euler_exponential_system_and_control_matrices(
            invalid_matrix, control_matrix, time_step
        )
    assert exception_information.typename == ValueError.__name__
    assert "exponential A matrix is singular" in str(
        exception_information.value
    )
    # Test no. 4
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.05,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.1,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    boundaries_1: List[Boundary] = [
        Boundary(
            id="kitchen-floor",
            label="Kitchen floor",
            side_1="kitchen",
            side_2="ground",
            area=10,
            azimuth=0,
            tilt=180,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-south",
            label="Kitchen exterior south",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-east",
            label="Kitchen exterior east",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=90,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-north",
            label="Kitchen exterior north",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-west",
            label="Kitchen exterior west",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=270,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-roof",
            label="Kitchen exterior roof",
            side_1="kitchen",
            side_2="boundary",
            area=10,
            azimuth=270,
            tilt=0,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_2, layer_1],
        ),
    ]
    space_1.boundaries = boundaries_1
    spaces: List[Space] = [space_1]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
    set_radiative_shares(spaces=spaces)
    system_matrix, control_matrix, state_indices, input_indices = (
        generate_system_and_control_matrices(
            spaces=spaces, boundaries=boundaries_1
        )
    )
    system_matrix_exponential, control_matrix_exponential = (
        generate_euler_exponential_system_and_control_matrices(
            system_matrix=system_matrix,
            control_matrix=control_matrix,
            time_step=3_600,
        )
    )


def test_generate_system_and_control_matrices() -> None:
    """Test the generate_system_and_control_matrices function."""
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-2",
            "label": "layer",
            "thermal_conductivity": 0.035,
            "specific_heat": 1.03,
            "density": 25,
            "thickness": 0.15,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    window_1: ElementObject = ElementObject.create_instance(
        class_name="Window",
        fields={
            "id": "window-1",
            "name": "window-1",
            "label": "window 1",
            "side_1": "kitchen",
            "side_2": "exterior",
            "boundary_id": "kitchen-exterior-south",
            "transmittance": 0.7,
            "u_value": 1.4,
            "x_length": 1.0,
            "y_length": 1.0,
            "emissivities": [0.85, 0.85],
            "absorption": 0.08,
        },
    )
    window_2: ElementObject = ElementObject.create_instance(
        class_name="Window",
        fields={
            "id": "window-2",
            "name": "window-2",
            "label": "window 2",
            "side_1": "exterior",
            "side_2": "kitchen",
            "boundary_id": "kitchen-exterior-west",
            "transmittance": 0.7,
            "u_value": 1.4,
            "x_length": 1.0,
            "y_length": 1.0,
            "emissivities": [0.85, 0.85],
            "absorption": 0.08,
        },
    )
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    space_2: Space = Space(
        id="living-room",
        label="living-room",
        volume=100,
        reference_area=40,
    )
    space_3: Space = Space(
        id="entrance",
        label="entrance",
        volume=5,
        reference_area=2,
    )
    boundary_1: Boundary = Boundary(
        id="kitchen-floor",
        label="Kitchen floor",
        side_1="kitchen",
        side_2="exterior",
        area=10,
        azimuth=0,
        tilt=180,
        spaces=[space_1],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_2: Boundary = Boundary(
        id="kitchen-exterior-south",
        label="Kitchen exterior south",
        side_1="kitchen",
        side_2="exterior",
        area=12.5,
        azimuth=0,
        tilt=90,
        spaces=[space_1],
        object_collection=[window_1],
        layers=[layer_1, layer_2],
    )
    boundary_3: Boundary = Boundary(
        id="kitchen-exterior-east",
        label="Kitchen exterior east",
        side_1="kitchen",
        side_2="exterior",
        area=2.5,
        azimuth=90,
        tilt=90,
        spaces=[space_1],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_4: Boundary = Boundary(
        id="kitchen-exterior-east-entrance",
        label="Kitchen to entrance",
        side_1="kitchen",
        side_2="entrance",
        area=2.5,
        azimuth=90,
        tilt=90,
        spaces=[space_1, space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_5: Boundary = Boundary(
        id="kitchen-exterior-north",
        label="Kitchen exterior north",
        side_1="kitchen",
        side_2="living-room",
        area=12.5,
        azimuth=180,
        tilt=90,
        spaces=[space_1],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_6: Boundary = Boundary(
        id="kitchen-exterior-west",
        label="Kitchen exterior west",
        side_1="kitchen",
        side_2="exterior",
        area=5,
        azimuth=270,
        tilt=90,
        spaces=[space_1],
        object_collection=[window_2],
        layers=[layer_1, layer_2],
    )
    boundary_7: Boundary = Boundary(
        id="kitchen-exterior-roof",
        label="Kitchen exterior roof",
        side_1="kitchen",
        side_2="exterior",
        area=10,
        azimuth=0,
        tilt=0,
        spaces=[space_1],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundaries_1: List[Boundary] = [
        boundary_1,
        boundary_2,
        boundary_3,
        boundary_4,
        boundary_5,
        boundary_6,
        boundary_7,
    ]
    space_1.boundaries = boundaries_1
    boundary_8: Boundary = Boundary(
        id="living-room-floor",
        label="Living room floor",
        side_1="living-room",
        side_2="exterior",
        area=40,
        azimuth=0,
        tilt=180,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_9: Boundary = Boundary(
        id="living-room-exterior-south",
        label="Living room exterior south",
        side_1="living-room",
        side_2="kitchen",
        area=12.5,
        azimuth=0,
        tilt=90,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_10: Boundary = Boundary(
        id="living-room-exterior-east",
        label="Living room exterior east",
        side_1="living-room",
        side_2="exterior",
        area=17.5,
        azimuth=90,
        tilt=90,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_11: Boundary = Boundary(
        id="living-room-exterior-east-entrance",
        label="Living room to entrance",
        side_1="living-room",
        side_2="entrance",
        area=2.5,
        azimuth=90,
        tilt=90,
        spaces=[space_2, space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_12: Boundary = Boundary(
        id="living-room-exterior-north",
        label="Living room exterior north",
        side_1="living-room",
        side_2="exterior",
        area=12.5,
        azimuth=180,
        tilt=90,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_13: Boundary = Boundary(
        id="living-room-exterior-west",
        label="Living room exterior west",
        side_1="living-room",
        side_2="exterior",
        area=20,
        azimuth=270,
        tilt=90,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_14: Boundary = Boundary(
        id="living-room-exterior-roof",
        label="Living room exterior roof",
        side_1="living-room",
        side_2="exterior",
        area=40,
        azimuth=0,
        tilt=0,
        spaces=[space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundaries_2: List[Boundary] = [
        boundary_8,
        boundary_9,
        boundary_10,
        boundary_11,
        boundary_12,
        boundary_13,
        boundary_14,
    ]
    boundary_15: Boundary = Boundary(
        id="entrance-floor",
        label="Entrance floor",
        side_1="exterior",
        side_2="entrance",
        area=2,
        azimuth=0,
        tilt=180,
        spaces=[space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_16: Boundary = Boundary(
        id="entrance-exterior-south",
        label="Entrance exterior south",
        side_1="exterior",
        side_2="entrance",
        area=2.5,
        azimuth=0,
        tilt=90,
        spaces=[space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_17: Boundary = Boundary(
        id="entrance-exterior-east",
        label="Entrance exterior east",
        side_1="exterior",
        side_2="entrance",
        area=5,
        azimuth=90,
        tilt=90,
        spaces=[space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_18: Boundary = Boundary(
        id="entrance-exterior-north",
        label="Entrance exterior north",
        side_1="exterior",
        side_2="entrance",
        area=2.5,
        azimuth=180,
        tilt=90,
        spaces=[space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_19: Boundary = Boundary(
        id="entrance-exterior-west-kitchen",
        label="Entrance to kitchen",
        side_1="kitchen",
        side_2="entrance",
        area=2.5,
        azimuth=270,
        tilt=90,
        spaces=[space_1, space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_20: Boundary = Boundary(
        id="entrance-exterior-west-living-room",
        label="Entrance to living room",
        side_2="living-room",
        side_1="entrance",
        area=2.5,
        azimuth=270,
        tilt=90,
        spaces=[space_3, space_2],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundary_21: Boundary = Boundary(
        id="entrance-exterior-roof",
        label="Entrance exterior roof",
        side_1="exterior",
        side_2="entrance",
        area=5,
        azimuth=0,
        tilt=0,
        spaces=[space_3],
        object_collection=[],
        layers=[layer_1, layer_2],
    )
    boundaries_3: List[Boundary] = [
        boundary_15,
        boundary_16,
        boundary_17,
        boundary_18,
        boundary_19,
        boundary_20,
        boundary_21,
    ]
    space_1.boundaries = boundaries_1
    space_2.boundaries = boundaries_2
    space_3.boundaries = boundaries_3
    spaces: List[Space] = [space_1, space_2, space_3]
    boundaries: List[Boundary] = [
        boundary_1,
        boundary_2,
        boundary_3,
        boundary_4,
        boundary_5,
        boundary_6,
        boundary_7,
        boundary_8,
        boundary_9,
        boundary_10,
        boundary_11,
        boundary_12,
        boundary_13,
        boundary_14,
        boundary_15,
        boundary_16,
        boundary_17,
        boundary_18,
        boundary_19,
        boundary_20,
        boundary_21,
    ]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
    # TODO: Add that to project_data
    for boundary_index, boundary in enumerate(boundaries):
        windows: List[BoundaryObject] = [
            boundary_object
            for boundary_object in boundary.object_collection
            if boundary_object.__class__.__name__.lower() == "window"
        ]
        for window in windows:
            window.side_1 = boundary.side_1
            window.side_2 = boundary.side_2
            window.tilt = boundary.tilt
            window.azimuth = boundary.azimuth
            window.boundary_number = boundary_index
            window.boundary_id = boundary.id
            window.area = window.x_length * window.y_length
    set_radiative_shares(spaces=spaces)
    system_matrix, control_matrix, state_indices, input_indices = (
        generate_system_and_control_matrices(
            spaces=spaces, boundaries=boundaries
        )
    )
    assert isinstance(system_matrix, ndarray) is True
    assert system_matrix.shape == (94, 94)
    assert isinstance(control_matrix, ndarray) is True
    assert control_matrix.shape == (94, 88)
    assert isinstance(state_indices, dict) is True
    assert isinstance(input_indices, dict) is True


def test_get_states_from_index() -> None:
    """Test the get_states_from_index function."""
    states: ndarray = get_states_from_index(
        states=np.array(
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
                19.0,
                20.0,
                21.0,
                22.0,
            ]
        ),
        index_states={
            "boundaries": {"start_index": 0, "n_elements": 8},
            "windows": {"start_index": 6, "n_elements": 2},
            "spaces_mean_radiant": {"start_index": 8, "n_elements": 2},
            "spaces_air": {"start_index": 10, "n_elements": 2},
        },
        label="spaces_air",
    )
    assert isinstance(states, ndarray) is True
    assert states[0] == 20.0
    assert states[1] == 21.0


def test_get_window_u_value() -> None:
    """Test get_window_u_value function."""
    window_u_value: float = get_window_u_value(
        resistance_window=0.8,
        h_rad_ext=12.5,
        h_rad_int=3.5,
        h_conv_ext=8.0,
        h_conv_int=2.4,
    )
    assert window_u_value == pytest.approx(1.71, abs=0.025)
    window_u_value = get_window_u_value(
        resistance_window=0.0,
        h_rad_ext=12.5,
        h_rad_int=3.5,
        h_conv_ext=8.0,
        h_conv_int=2.4,
    )
    assert window_u_value == pytest.approx(0.01, abs=0.025)
    window_u_value = get_window_u_value(
        resistance_window="0.0",
        h_rad_ext="0.0",
        h_rad_int="0.0",
        h_conv_ext="0.0",
        h_conv_int="0.0",
    )
    assert window_u_value == pytest.approx(0.01, abs=0.025)
    window_u_value = get_window_u_value(
        resistance_window=0.0,
        h_rad_ext=0.0,
        h_rad_int=0.0,
        h_conv_ext=0.0,
        h_conv_int=0.0,
    )
    assert window_u_value == pytest.approx(0.01, abs=0.025)
    window_u_value = get_window_u_value(
        resistance_window=2.0,
        h_rad_ext=12.5,
        h_rad_int=3.5,
        h_conv_ext=None,
        h_conv_int=2.4,
    )
    assert window_u_value == pytest.approx(0.01, abs=0.025)


def test_run_state_space() -> None:
    """Test the run_state_space function."""
    states: ndarray = run_state_space(
        system_matrix=np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 2.0, 0.0],
                [0.0, 0.0, 3.0],
            ]
        ),
        control_matrix=np.array(
            [
                [1.0, 4.0],
                [2.0, 5.0],
                [3.0, 6.0],
            ]
        ),
        states=np.array([7.0, 8.0, 9.0]),
        input_signals=np.array([2.5, 3.5]),
    )
    expected_states: List[float] = [23.5, 38.5, 55.5]
    for index, state in enumerate(states):
        assert state == pytest.approx(expected_states[index], abs=0.25)


def test_set_boundary_discretization_properties() -> None:
    """Test set_boundary_discretization_properties function."""
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-2",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.1,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    boundary: Boundary = Boundary(
        id="kitchen-floor",
        label="Kitchen floor",
        side_1="kitchen",
        side_2="exterior",
        area=10,
        azimuth=0,
        tilt=0,
        object_collection=[],
        layers=[layer_1, layer_2, layer_2, layer_1],
    )
    assert set_boundary_discretization_properties(boundary=boundary) is None
    assert isinstance(boundary.resistances, ndarray) is True
    assert isinstance(boundary.thermal_masses, ndarray) is True
    assert boundary.u_value == pytest.approx(1.67, abs=0.05)
    assert boundary.thermal_masses[0] == pytest.approx(6_300, abs=1)
    assert boundary.resistances[1] == pytest.approx(0.15, abs=0.01)


def test_set_input_signals_from_index() -> None:
    """Test set_input_signals_from_index function."""
    input_signals: ndarray = np.array([2.5, 3.5, 4.5, 5.5])
    input_signals_indices: Dict[str, Dict[str, int]] = {
        "ground_temperature": {"start_index": 0, "n_elements": 1},
        "exterior_air_temperature": {"start_index": 1, "n_elements": 2},
    }
    assert (
        set_input_signals_from_index(
            input_signals=input_signals,
            input_signals_indices=input_signals_indices,
            label="ground_temperature",
            value_to_set=8.0,
            add=False,
        )
        is None
    )
    assert input_signals[0] == 8.0
    assert (
        set_input_signals_from_index(
            input_signals=input_signals,
            input_signals_indices=input_signals_indices,
            label="exterior_air_temperature",
            value_to_set=6.5,
            add=True,
        )
        is None
    )
    assert input_signals[1] == 10.0
    assert input_signals[2] == 11.0
    assert input_signals[3] == 5.5


def test_set_radiative_shares() -> None:
    """Test the set_radiative_shares function."""
    # Test no. 1
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-2",
            "label": "layer",
            "thermal_conductivity": 0.035,
            "specific_heat": 1.03,
            "density": 25,
            "thickness": 0.15,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    boundaries_1: List[Boundary] = [
        Boundary(
            id="kitchen-floor",
            label="Kitchen floor",
            side_1="kitchen",
            side_2="exterior",
            area=10,
            azimuth=0,
            tilt=180,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-south",
            label="Kitchen exterior south",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-east",
            label="Kitchen exterior east",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=90,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-north",
            label="Kitchen exterior north",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-west",
            label="Kitchen exterior west",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=270,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-roof",
            label="Kitchen exterior roof",
            side_1="kitchen",
            side_2="exterior",
            area=10,
            azimuth=0,
            tilt=0,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
    ]
    space_1.boundaries = boundaries_1
    spaces: List[Space] = [space_1]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
    assert set_radiative_shares(spaces=spaces) is None
    assert spaces[0].envelope_elements == {
        "kitchen-floor": {
            "type": "floor",
            "area": 10,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.642,
        },
        "kitchen-exterior-south": {
            "type": "other",
            "area": 12.5,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.0994,
        },
        "kitchen-exterior-east": {
            "type": "other",
            "area": 5,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.0398,
        },
        "kitchen-exterior-north": {
            "type": "other",
            "area": 12.5,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.0994,
        },
        "kitchen-exterior-west": {
            "type": "other",
            "area": 5,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.0398,
        },
        "kitchen-exterior-roof": {
            "type": "other",
            "area": 10,
            "side": "side_1",
            "u_value": 0.228,
            "radiative_share": 0.0796,
        },
    }
    # Test no. 2
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    boundaries_1: List[Boundary] = [
        Boundary(
            id="kitchen-floor",
            label="Kitchen floor",
            side_1="exterior",
            side_2="kitchen",
            area=10,
            azimuth=0,
            tilt=180,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-south",
            label="Kitchen exterior south",
            side_1="exterior",
            side_2="kitchen",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-east",
            label="Kitchen exterior east",
            side_1="exterior",
            side_2="kitchen",
            area=5,
            azimuth=90,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-north",
            label="Kitchen exterior north",
            side_1="exterior",
            side_2="kitchen",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-west",
            label="Kitchen exterior west",
            side_1="exterior",
            side_2="kitchen",
            area=5,
            azimuth=270,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
        Boundary(
            id="kitchen-exterior-roof",
            label="Kitchen exterior roof",
            side_1="exterior",
            side_2="kitchen",
            area=10,
            azimuth=0,
            tilt=0,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2, layer_1],
        ),
    ]
    space_1.boundaries = boundaries_1
    spaces: List[Space] = [space_1]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
    assert set_radiative_shares(spaces=spaces) is None
    assert spaces[0].envelope_elements == {
        "kitchen-floor": {
            "type": "floor",
            "area": 10,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.642,
        },
        "kitchen-exterior-south": {
            "type": "other",
            "area": 12.5,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.0994,
        },
        "kitchen-exterior-east": {
            "type": "other",
            "area": 5,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.0398,
        },
        "kitchen-exterior-north": {
            "type": "other",
            "area": 12.5,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.0994,
        },
        "kitchen-exterior-west": {
            "type": "other",
            "area": 5,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.0398,
        },
        "kitchen-exterior-roof": {
            "type": "other",
            "area": 10,
            "side": "side_2",
            "u_value": 0.2229,
            "radiative_share": 0.0796,
        },
    }
    # Test no. 3
    window_1: ElementObject = ElementObject.create_instance(
        class_name="Window",
        fields={
            "id": "window-1",
            "name": "window-1",
            "label": "window 1",
            "side_1": "kitchen",
            "side_2": "exterior",
            "area": 1.0,
            "boundary_id": "kitchen-exterior-south",
            "transmittance": 0.7,
            "u_value": 1.4,
        },
    )
    window_2: ElementObject = ElementObject.create_instance(
        class_name="Window",
        fields={
            "id": "window-2",
            "name": "window-2",
            "label": "window 2",
            "side_1": "exterior",
            "side_2": "kitchen",
            "area": 1.0,
            "boundary_id": "kitchen-exterior-west",
            "transmittance": 0.7,
            "u_value": 1.4,
        },
    )
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    space_2: Space = Space(
        id="living-room",
        label="living-room",
        volume=100,
        reference_area=40,
    )
    space_3: Space = Space(
        id="entrance",
        label="entrance",
        volume=5,
        reference_area=2,
    )
    boundaries_1: List[Boundary] = [
        Boundary(
            id="kitchen-floor",
            label="Kitchen floor",
            side_1="kitchen",
            side_2="exterior",
            area=10,
            azimuth=0,
            tilt=180,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-south",
            label="Kitchen exterior south",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_1],
            object_collection=[window_1],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-east",
            label="Kitchen exterior east",
            side_1="kitchen",
            side_2="exterior",
            area=2.5,
            azimuth=90,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-east-entrance",
            label="Kitchen to entrance",
            side_1="kitchen",
            side_2="entrance",
            area=2.5,
            azimuth=90,
            tilt=90,
            spaces=[space_1, space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-north",
            label="Kitchen exterior north",
            side_1="kitchen",
            side_2="living-room",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-west",
            label="Kitchen exterior west",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=270,
            tilt=90,
            spaces=[space_1],
            object_collection=[window_2],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-roof",
            label="Kitchen exterior roof",
            side_1="kitchen",
            side_2="exterior",
            area=10,
            azimuth=0,
            tilt=0,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
    ]
    space_1.boundaries = boundaries_1
    boundaries_2: List[Boundary] = [
        Boundary(
            id="living-room-floor",
            label="Living room floor",
            side_1="living-room",
            side_2="exterior",
            area=40,
            azimuth=0,
            tilt=180,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-south",
            label="Living room exterior south",
            side_1="living-room",
            side_2="kitchen",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-east",
            label="Living room exterior east",
            side_1="living-room",
            side_2="exterior",
            area=17.5,
            azimuth=90,
            tilt=90,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-east-entrance",
            label="Living room to entrance",
            side_1="living-room",
            side_2="entrance",
            area=2.5,
            azimuth=90,
            tilt=90,
            spaces=[space_2, space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-north",
            label="Living room exterior north",
            side_1="living-room",
            side_2="exterior",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-west",
            label="Living room exterior west",
            side_1="living-room",
            side_2="exterior",
            area=20,
            azimuth=270,
            tilt=90,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="living-room-exterior-roof",
            label="Living room exterior roof",
            side_1="living-room",
            side_2="exterior",
            area=40,
            azimuth=0,
            tilt=0,
            spaces=[space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
    ]
    boundaries_3: List[Boundary] = [
        Boundary(
            id="entrance-floor",
            label="Entrance floor",
            side_1="exterior",
            side_2="entrance",
            area=2,
            azimuth=0,
            tilt=180,
            spaces=[space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-south",
            label="Entrance exterior south",
            side_1="exterior",
            side_2="entrance",
            area=2.5,
            azimuth=0,
            tilt=90,
            spaces=[space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-east",
            label="Entrance exterior east",
            side_1="exterior",
            side_2="entrance",
            area=5,
            azimuth=90,
            tilt=90,
            spaces=[space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-north",
            label="Entrance exterior north",
            side_1="exterior",
            side_2="entrance",
            area=2.5,
            azimuth=180,
            tilt=90,
            spaces=[space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-west-kitchen",
            label="Entrance to kitchen",
            side_1="kitchen",
            side_2="entrance",
            area=2.5,
            azimuth=270,
            tilt=90,
            spaces=[space_1, space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-west-living-room",
            label="Entrance to living room",
            side_2="living-room",
            side_1="entrance",
            area=2.5,
            azimuth=270,
            tilt=90,
            spaces=[space_3, space_2],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="entrance-exterior-roof",
            label="Entrance exterior roof",
            side_1="exterior",
            side_2="entrance",
            area=5,
            azimuth=0,
            tilt=0,
            spaces=[space_3],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
    ]
    space_1.boundaries = boundaries_1
    space_2.boundaries = boundaries_2
    space_3.boundaries = boundaries_3
    spaces: List[Space] = [space_1, space_2, space_3]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
    assert set_radiative_shares(spaces=spaces) is None
    # Test no. 4
    with pytest.raises(ValueError) as exception_information:
        space_1: Space = Space(
            id="kitchen",
            label="kitchen",
            volume=25,
            reference_area=10,
        )
        boundaries_1: List[Boundary] = [
            Boundary(
                id="kitchen-floor",
                label="Kitchen floor",
                side_1="kitchen",
                side_2="exterior",
                area=10,
                azimuth=0,
                tilt=180,
                spaces=[space_1],
                object_collection=[],
                layers=[layer_1, layer_2],
            ),
            Boundary(
                id="kitchen-floor-2",
                label="Kitchen floor 2",
                side_1="kitchen",
                side_2="exterior",
                area=12.5,
                azimuth=0,
                tilt=180,
                spaces=[space_1],
                object_collection=[],
                layers=[layer_1, layer_2],
            ),
            Boundary(
                id="kitchen-exterior-east",
                label="Kitchen exterior east",
                side_1="kitchen",
                side_2="exterior",
                area=5,
                azimuth=90,
                tilt=90,
                spaces=[space_1],
                object_collection=[],
                layers=[layer_1, layer_2],
            ),
            Boundary(
                id="kitchen-exterior-north",
                label="Kitchen exterior north",
                side_1="kitchen",
                side_2="exterior",
                area=12.5,
                azimuth=180,
                tilt=90,
                spaces=[space_1],
                object_collection=[],
                layers=[layer_1, layer_2],
            ),
        ]
        space_1.boundaries = boundaries_1
        spaces: List[Space] = [space_1]
        for space in spaces:
            for boundary in space.boundaries:
                set_boundary_discretization_properties(boundary=boundary)
        set_radiative_shares(spaces=spaces)
    assert exception_information.typename == ValueError.__name__
    assert (
        "Radiative share calculation is wrong. The sum of all shares must be equal to 1"
        in str(exception_information.value)
    )


def test_set_u_values() -> None:
    """Test the set_u_values function."""
    window_1: ElementObject = ElementObject.create_instance(
        class_name="Window",
        fields={
            "name": "window-1",
            "id": "window-1",
            "label": "window 1",
            "side_1": "kitchen",
            "side_2": "exterior",
            "area": 1.0,
            "boundary_id": "kitchen-exterior-south",
            "transmittance": 0.7,
            "u_value": 1.4,
            "tilt": 90,
            "emissivities": [0.9, 0.9],
            "boundary_number": 1,
            "absorption": 0.2,
        },
    )
    space_1: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=25,
        reference_area=10,
    )
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.05,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "layer-1",
            "label": "layer",
            "thermal_conductivity": 0.5,
            "specific_heat": 1_050,
            "density": 2_400,
            "thickness": 0.1,
            "emissivity": 0.9,
            "albedo": 0.7,
        },
    )
    boundaries_1: List[Boundary] = [
        Boundary(
            id="kitchen-floor",
            label="Kitchen floor",
            side_1="kitchen",
            side_2="ground",
            area=10,
            azimuth=0,
            tilt=180,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-south",
            label="Kitchen exterior south",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=0,
            tilt=90,
            spaces=[space_1],
            object_collection=[window_1],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-east",
            label="Kitchen exterior east",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=90,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-north",
            label="Kitchen exterior north",
            side_1="kitchen",
            side_2="exterior",
            area=12.5,
            azimuth=180,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-west",
            label="Kitchen exterior west",
            side_1="kitchen",
            side_2="exterior",
            area=5,
            azimuth=270,
            tilt=90,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
        Boundary(
            id="kitchen-exterior-roof",
            label="Kitchen exterior roof",
            side_1="kitchen",
            side_2="boundary",
            area=10,
            azimuth=0,
            tilt=0,
            spaces=[space_1],
            object_collection=[],
            layers=[layer_1, layer_2],
        ),
    ]
    space_1.boundaries = boundaries_1
    spaces: List[Space] = [space_1]
    for space in spaces:
        for boundary in space.boundaries:
            set_boundary_discretization_properties(boundary)
    set_radiative_shares(spaces=spaces)
    assert set_u_values(spaces=spaces) is None
    assert space_1.u_wall == pytest.approx(2.12, abs=0.025)
    assert space_1.wall_area == pytest.approx(55.0, abs=0.1)
    assert space_1.u_window == pytest.approx(1.4, abs=0.025)
    assert space_1.window_area == pytest.approx(1.0, abs=0.1)


if __name__ == "__main__":
    test_generate_euler_exponential_system_and_control_matrices()
    test_generate_system_and_control_matrices()
    test_get_states_from_index()
    test_get_window_u_value()
    test_run_state_space()
    test_set_boundary_discretization_properties()
    test_set_input_signals_from_index()
    test_set_radiative_shares()
    test_set_u_values()
