"""
Test for the `dataset.py` module.
"""

import logging
from typing import Any, Dict, Iterator, List

import pytest
from pytest import LogCaptureFixture, MonkeyPatch

from colibri.datamodel.dataset import DataSet
from colibri.utils.exceptions_utils import UserInputError


def test_dataset(caplog: LogCaptureFixture, monkeypatch: MonkeyPatch) -> None:
    """Test the DataSet class."""
    # Test 1
    inputs: Iterator = iter(
        [
            "no",
            "None",
            "2",
            "55",
            "None",
            "None",
            "0.1",
            "0.25",
            "200",
            "1234",
            "concrete",
            "0.65",
            "0.2",
            "0.3",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    modules: List[str] = [
        "AcvExploitationOnly",
        "LimitedGenerator",
        "OccupantModel",
        "LayerWallLosses",
        "ThermalSpaceSimplified",
        "WeatherModel",
    ]
    type_name: str = "Layer"
    archetype_id: str = "layer-001"
    dataset: DataSet = DataSet(modules=modules)
    assert dataset.modules == modules
    dataset.add_archetype(type_name=type_name, archetype_id=archetype_id)
    assert dataset.unique_ids == ["layer-001"]
    assert dataset.archetype_collection[f"{type_name}_types"][archetype_id] == {
        "lca_impact_properties": "None",
        "installation_year": "2",
        "label": "layer-001",
        "service_life": "55",
        "constitutive_materials": "None",
        "end_of_life_properties": "None",
        "id": "layer-001",
        "thickness": "0.1",
        "thermal_conductivity": "0.25",
        "specific_heat": "200",
        "density": "1234",
        "material_type": "concrete",
        "emissivity": "0.65",
        "light_reflectance": "0.2",
        "albedo": "0.3",
    }
    with caplog.at_level(logging.INFO):
        assert (
            dataset.describe(
                category="Archetypes",
                type_name="Layer",
                parameter_name="thermal_conductivity",
            )
            is None
        )
        assert "thermal_conductivity" in caplog.text
        assert "Thermal conductivity of the layer." in caplog.text
        assert "format: float" in caplog.text
        assert "unit: W/(m.K)" in caplog.text
    with caplog.at_level(logging.INFO):
        assert dataset.doc() is None
        assert "add_archetype" in caplog.text
        assert "create_segment_and_compute_area_from_coordinates" in caplog.text
        assert "add_structure_object" in caplog.text
        assert "link_boundaries" in caplog.text
    inputs: Iterator = iter(["no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset.add_archetype(
        type_name=type_name,
        archetype_id="layer-002",
        thickness=0.15,
        thermal_conductivity=0.035,
        density=876,
        material_type="concrete",
        specific_heat=213,
        lca_impact_properties=None,
        installation_year=1,
        service_life=55,
        constitutive_materials=None,
        end_of_life_properties=None,
        emissivity=0.65,
        light_reflectance=0.2,
        albedo=0.3,
    )
    assert list(dataset.archetype_collection[f"{type_name}_types"].keys()) == [
        "layer-001",
        "layer-002",
    ]
    inputs: Iterator = iter(["no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with pytest.raises(Exception) as exception_information:
        dataset.add_archetype(
            type_name=type_name,
            archetype_id="layer-002",
            thickness=-0.15,
            thermal_conductivity=0.035,
            density=876,
            material_type="concrete",
            specific_heat=213,
            lca_impact_properties=None,
            installation_year=1,
            service_life=55,
            constitutive_materials=None,
            end_of_life_properties=None,
            emissivity=0.65,
            light_reflectance=0.2,
            albedo=0.3,
        )
    assert exception_information.typename == UserInputError.__name__
    assert "-0.15 for thickness is below its minimum value of 0." in str(
        exception_information.value
    )
    inputs: Iterator = iter(
        [
            "no",
            "no",
            "None",
            "2",
            "55",
            "None",
            "None",
            "0.5",
            "0.12",
            "200",
            "1234",
            "concrete",
            "0.65",
            "0.2",
            "0.3",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset.add_archetype(type_name=type_name)
    # Test 2
    inputs: Iterator = iter(
        [
            "no",
            "None",
            "2",
            "55",
            "None",
            "None",
            "0.1",
            "0.25",
            "0.4",
            "1234",
            "concrete",
            "0.65",
            "0.2",
            "0.3",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    modules_2: List[str] = [
        "AcvExploitationOnly",
        "InfinitePowerGenerator",
        "OccupantModel",
        "SimplifiedWallLosses",
        "ThermalSpaceSimplified",
        "WeatherModel",
    ]
    dataset_2: DataSet = DataSet(modules=modules_2)
    assert dataset_2.modules == modules_2
    with pytest.raises(Exception) as exception_information:
        dataset_2.add_archetype(
            type_name="WrongArchetypeName", archetype_id="layer-001"
        )
    assert exception_information.typename == ValueError.__name__
    assert (
        "WrongArchetypeName is not a available archetype. Please, choose among: ['Boundary', 'Layer', 'Emitter']."
        in str(exception_information.value)
    )
    # Test 3
    dataset_3: DataSet = DataSet(modules=modules)
    with caplog.at_level(logging.INFO):
        assert dataset_3.describe(type_name="Layer") is None
        assert (
            "List of parameters for the Layer (Archetype) object" in caplog.text
        )
        assert "thickness: Thickness of the layer. [m]" in caplog.text
        assert (
            "thermal_conductivity: Thermal conductivity of the layer. [W/(m.K)]"
            in caplog.text
        )
    # Test 4
    dataset_4: DataSet = DataSet(modules=modules, verbose=True)
    inputs: Iterator = iter(["no", "no", "default to all"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset_4.add_archetype(type_name=type_name)
    # Test 5
    dataset_5: DataSet = DataSet(modules=modules, verbose=True)
    dataset_5.unique_ids = ["layer-id-1234"]
    inputs: Iterator = iter(["layer-id-1234", "no", "default to all"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset_5.add_archetype(type_name=type_name)
    # Test 6
    dataset_6: DataSet = DataSet(modules=modules, verbose=True)
    dataset_6.archetype_collection["Layer_types"] = {
        "layer-id-1234": {
            "id": "layer-id-1234",
            "label": "layer-id-1234",
            "lca_impact_properties": None,
            "installation_year": 1,
            "service_life": 50,
            "constitutive_materials": [
                {"share": 1, "material_type": "concrete"}
            ],
            "end_of_life_properties": None,
            "thickness": 0.3,
            "thermal_conductivity": 1.75,
            "specific_heat": 900,
            "density": 2500,
            "material_type": "concrete",
            "emissivity": 0.92,
            "light_reflectance": 0.8,
            "albedo": 0.25,
        },
    }
    inputs: Iterator = iter(["layer-id-1234", "no", "default to all", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset_6.add_archetype(type_name=type_name)
    assert dataset_6.compute_segment_length(
        point_1=[2, 4], point_2=[4, 6]
    ) == pytest.approx(2.83, abs=0.05)
    assert dataset_6.compute_segment_length(
        point_1=[2, 3], point_2=[9, 11]
    ) == pytest.approx(10.63, abs=0.05)
    with pytest.raises(UserInputError) as exception_information:
        ordered_coordinates = [[0, 0], [0, 2.5], [4, 2.5], [4, 0]]
        ordered_names = (
            [
                "s_mur_salon_ouest_et_mur_salon_nord",
                "s_mur_salon_ouest_plafond",
                "s_mur_salon_ouest_et_mur_salon_sud",
            ],
        )
        dataset_6.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=ordered_coordinates, ordered_names=ordered_names
        )
    assert exception_information.typename == UserInputError.__name__
    assert "Segment names ('ordered_names') has not the same length" in str(
        exception_information.value
    )
    inputs: Iterator = iter(
        [
            "[0,0]",
            "[0,2.5]",
            "[4, 2.5]",
            "toto",
            "[4, 0]",
            "end",
            "s_mur_salon_ouest_et_mur_salon_nord",
            "no",
            "no to all",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dataset_6.create_segment_and_compute_area_from_coordinates(
        ordered_coordinates=None, ordered_names=None
    )
    # Test 7
    number_of_elements_to_be_added: int = 27
    house_1: DataSet = DataSet(modules=modules)
    inputs: Iterator = iter(["default to all"] * number_of_elements_to_be_added)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="beton_1",
        label="béton 20cm",
        thickness=0.2,
    )
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="isolant_1",
        label="isolant 15cm pour mur verticaux",
        thickness=0.15,
        thermal_conductivity=0.035,
        specific_heat=1030,
        density=25,
        material_type="insulation",
        constitutive_material_type="rock wood",
    )
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="isolant_toiture",
        label="isolant 10cm pour toiture",
        thickness=0.1,
        thermal_conductivity=0.035,
        specific_heat=1030,
        density=25,
        material_type="insulation",
        constitutive_material_type="rock wood",
    )
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="isolant_plancher",
        label="isolant 5cm pour plancher",
        thickness=0.05,
        thermal_conductivity=0.035,
        specific_heat=1030,
        density=25,
        material_type="insulation",
        constitutive_material_type="rock wood",
    )
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="vide_10",
        label="vide 10cm",
        thickness=0.1,
        thermal_conductivity=0.025,
        specific_heat=1000,
        density=1.293,
        material_type="insulation",
        constitutive_material_type="air",
    )
    house_1.add_archetype(
        type_name="Layer",
        archetype_id="ba_13",
        label="BA13",
        thickness=0.013,
        thermal_conductivity=0.25,
        specific_heat=1000,
        density=850,
        material_type="plaster",
    )
    house_1.add_archetype(
        type_name="Boundary",
        archetype_id="mur_exterieur_1",
        label="Mur exterieur",
        layers=[
            {"type": "Layer", "type_id": "isolant_1"},
            {"type": "Layer", "type_id": "beton_1"},
        ],
    )
    house_1.add_archetype(
        type_name="Boundary",
        archetype_id="toiture_1",
        label="Plancher haut",
        layers=[
            {"type": "Layer", "type_id": "beton_1"},
            {"type": "Layer", "type_id": "isolant_toiture"},
        ],
    )
    house_1.add_archetype(
        type_name="Boundary",
        archetype_id="plancher_1",
        label="Plancher bas",
        layers=[
            {"type": "Layer", "type_id": "isolant_plancher"},
            {"type": "Layer", "type_id": "beton_1"},
        ],
    )
    house_1.add_archetype(
        type_name="Boundary",
        archetype_id="cloison_1",
        label="Cloison BA13",
        layers=[
            {"type": "Layer", "type_id": "ba_13"},
            {"type": "Layer", "type_id": "vide_10"},
            {"type": "Layer", "type_id": "ba_13"},
        ],
    )
    with caplog.at_level(logging.INFO):
        assert dataset_3.describe(type_name="Space") is None
        assert (
            "List of parameters for the Space (StructureObject) object"
            in caplog.text
        )
        assert "id: Unique identifier (ID) of the space. [-]" in caplog.text
        assert "q_needs: Needs of the space. [W]" in caplog.text
    # Spaces
    house_1.add_structure_object(
        type_name="Space",
        structure_object_id="living_room_1",
        label="salon",
        reference_area=20.9,
        volume=20.9 * 2.5,
        altitude=0,
        use="living room",
    )
    house_1.add_structure_object(
        type_name="Space",
        structure_object_id="kitchen_1",
        label="cuisine",
        reference_area=9.52,
        volume=9.52 * 2.5,
        altitude=0,
        use="kitchen",
    )
    # Boundaries and segments
    segments_mur_salon_sud, area_mur_salon_sud = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
            ordered_names=[
                "s_mur_salon_sud_et_mur_salon_ouest",
                "s_mur_salon_sud_plafond",
                "s_mur_salon_sud_et_mur_cuisine_sud",
                "s_mur_salon_sud_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_salon_sud_1",
        label="Mur salon sud",
        archetype_id="mur_exterieur_1",
        azimuth=180,
        side_1="exterior",
        side_2="living_room_1",
        tilt=90,
        segments=segments_mur_salon_sud,
        area=area_mur_salon_sud,
        origin_3d=(0, 0, 0),
    )
    segments_mur_salon_ouest, area_mur_salon_ouest = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [4, 2.5], [4, 0]],
            ordered_names=[
                "s_mur_salon_ouest_et_mur_salon_nord",
                "s_mur_salon_ouest_plafond",
                "s_mur_salon_ouest_et_mur_salon_sud",
                "s_mur_salon_ouest_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_salon_ouest_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon ouest",
        azimuth=270,
        side_1="exterior",
        side_2="living_room_1",
        tilt=90,
        segments=segments_mur_salon_ouest,
        area=area_mur_salon_ouest,
        origin_3d=(0, 4, 0),
    )
    segments_mur_salon_nord, area_mur_salon_nord = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
            ordered_names=[
                "s_mur_salon_nord_et_mur_salon_est",
                "s_mur_salon_nord_plafond",
                "s_mur_salon_nord_et_mur_salon_ouest",
                "s_mur_salon_nord_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_salon_nord_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon nord",
        azimuth=0,
        side_1="exterior",
        side_2="living_room_1",
        tilt=90,
        segments=segments_mur_salon_nord,
        area=area_mur_salon_nord,
        origin_3d=(6, 4, 0),
    )
    segments_mur_salon_est, area_mur_salon_est = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
            ordered_names=[
                "s_mur_salon_est_et_mur_salon_cuisine",
                "s_mur_salon_est_plafond",
                "s_mur_salon_est_et_mur_salon_nord",
                "s_mur_salon_est_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_salon_est_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon nord",
        azimuth=90,
        side_1="exterior",
        side_2="living_room_1",
        tilt=90,
        segments=segments_mur_salon_est,
        area=area_mur_salon_est,
        origin_3d=(6, 2, 0),
    )
    segments_mur_salon_cuisine, area_mur_salon_cuisine = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
            ordered_names=[
                "s_mur_salon_cuisine_et_mur_salon_sud",
                "s_mur_salon_cuisine_plafond",
                "s_mur_salon_cuisine_et_mur_salon_est",
                "s_mur_salon_cuisine_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_salon_cuisine",
        archetype_id="cloison_1",
        label="Mur salon nord",
        azimuth=90,
        side_1="kitchen_1",
        side_2="living_room_1",
        tilt=90,
        segments=segments_mur_salon_cuisine,
        area=area_mur_salon_cuisine,
        origin_3d=(6, 0, 0),
    )
    segments_mur_cuisine_nord, area_mur_cuisine_nord = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
            ordered_names=[
                "s_mur_cuisine_nord_et_mur_cuisine_est",
                "s_mur_cuisine_nord_plafond",
                "s_mur_cuisine_nord_et_mur_salon_est",
                "s_mur_cuisine_nord_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_cuisine_nord_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon nord",
        azimuth=0,
        side_1="exterior",
        side_2="kitchen_1",
        tilt=90,
        segments=segments_mur_cuisine_nord,
        area=area_mur_cuisine_nord,
        origin_3d=(12, 2, 0),
    )
    segments_mur_cuisine_est, area_mur_cuisine_est = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
            ordered_names=[
                "s_mur_cuisine_est_et_mur_cuisine_sud",
                "s_mur_cuisine_est_plafond",
                "s_mur_cuisine_est_et_mur_cuisine_nord",
                "s_mur_cuisine_est_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_cuisine_est_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon nord",
        azimuth=90,
        side_1="exterior",
        side_2="kitchen_1",
        tilt=90,
        segments=segments_mur_cuisine_est,
        area=area_mur_cuisine_est,
        origin_3d=(12, 0, 0),
    )
    segments_mur_cuisine_sud, area_mur_cuisine_sud = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
            ordered_names=[
                "s_mur_cuisine_sud_et_mur_salon_sud",
                "s_mur_cuisine_sud_plafond",
                "s_mur_cuisine_sud_et_mur_cuisine_est",
                "s_mur_cuisine_sud_plancher",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="mur_cuisine_sud_1",
        archetype_id="mur_exterieur_1",
        label="Mur salon nord",
        azimuth=180,
        side_1="exterior",
        side_2="kitchen_1",
        tilt=90,
        segments=segments_mur_cuisine_sud,
        area=area_mur_cuisine_sud,
        origin_3d=(6, 0, 0),
    )
    segments_plafond_salon, area_plafond_salon = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 4], [6, 4], [6, 2], [6, 0]],
            ordered_names=[
                "s_plafond_mur_salon_ouest",
                "s_plafond_mur_salon_nord",
                "s_plafond_mur_salon_est",
                "s_plafond_salon_mur_cuisine",
                "s_plafond_mur_salon_sud",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="plafond_salon",
        archetype_id="toiture_1",
        label="Plafond salon",
        azimuth=0,
        side_1="exterior",
        side_2="living_room_1",
        tilt=0,
        segments=segments_plafond_salon,
        area=area_plafond_salon,
        origin_3d=(0, 0, 2.5),
    )
    segments_plancher_salon, area_plancher_salon = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 4], [6, 4], [6, 2], [6, 0]],
            ordered_names=[
                "s_plancher_mur_salon_ouest",
                "s_plancher_mur_salon_nord",
                "s_plancher_mur_salon_est",
                "s_plancher_mur_salon_cuisine",
                "s_plancher_mur_salon_sud",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="plancher_salon",
        archetype_id="plancher_1",
        label="Plancher salon",
        azimuth=0,
        side_1="living_room_1",
        side_2="ground",
        tilt=180,
        segments=segments_plancher_salon,
        area=area_plancher_salon,
        origin_3d=(0, 0, 0),
    )
    segments_plafond_cuisine, area_plafond_cuisine = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2], [6, 2], [6, 0]],
            ordered_names=[
                "s_plafond_cuisine_mur_salon_cuisine",
                "s_plafond_mur_cuisine_nord",
                "s_plafond_mur_cuisine_est",
                "s_plafond_mur_cuisine_sud",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="plafond_cuisine",
        archetype_id="toiture_1",
        label="Plafond cuisine",
        azimuth=0,
        side_1="exterior",
        side_2="kitchen_1",
        tilt=0,
        segments=segments_plafond_cuisine,
        area=area_plafond_cuisine,
        origin_3d=(0, 6, 2.5),
    )
    segments_plancher_cuisine, area_plancher_cuisine = (
        house_1.create_segment_and_compute_area_from_coordinates(
            ordered_coordinates=[[0, 0], [0, 2], [6, 2], [6, 0]],
            ordered_names=[
                "s_plancher_mur_salon_cuisine",
                "s_plancher_mur_cuisine_nord",
                "s_plancher_mur_cuisine_est",
                "s_plancher_mur_cuisine_sud",
            ],
        )
    )
    house_1.add_structure_object(
        type_name="Boundary",
        structure_object_id="plancher_cuisine",
        archetype_id="plancher_1",
        label="Plafond cuisine",
        azimuth=0,
        side_1="kitchen_1",
        side_2="ground",
        tilt=0,
        segments=segments_plancher_cuisine,
        area=area_plancher_cuisine,
        origin_3d=(0, 6, 2.5),
    )
    # Junctions
    house_1.link_boundaries(
        boundary_ids=["mur_salon_sud_1", "mur_salon_ouest_1"],
        segment_ids=[
            "s_mur_salon_sud_et_mur_salon_ouest",
            "s_mur_salon_ouest_et_mur_salon_sud",
        ],
        id="j_mur_salon_sud_et_mur_salon_ouest",
    )
    house_1.link_boundaries(
        boundary_ids=["mur_salon_ouest_1", "mur_salon_nord_1"],
        segment_ids=[
            "s_mur_salon_ouest_et_mur_salon_nord",
            "s_mur_salon_nord_et_mur_salon_ouest",
        ],
        id="j_mur_salon_ouest_et_mur_salon_nord",
    )
    house_1.link_boundaries(
        boundary_ids=["mur_salon_nord_1", "mur_salon_est_1"],
        segment_ids=[
            "s_mur_salon_nord_et_mur_salon_est",
            "s_mur_salon_est_et_mur_salon_nord",
        ],
        id="j_mur_salon_nord_et_mur_salon_est",
    )
    house_1.link_boundaries(
        boundary_ids=[
            "mur_salon_est_1",
            "mur_cuisine_nord_1",
            "mur_salon_cuisine",
        ],
        segment_ids=[
            "s_mur_salon_est_et_mur_salon_cuisine",
            "s_mur_cuisine_nord_et_mur_salon_est",
            "s_mur_salon_cuisine_et_mur_salon_est",
        ],
        id="j_mur_salon_est_et_mur_salon_cuisine",
    )
    house_1.link_boundaries(
        boundary_ids=["mur_cuisine_nord_1", "mur_cuisine_est_1"],
        segment_ids=[
            "s_mur_cuisine_nord_et_mur_cuisine_est",
            "s_mur_cuisine_est_et_mur_cuisine_nord",
        ],
        id="j_mur_cuisine_nord_et_mur_cuisine_est",
    )
    house_1.link_boundaries(
        boundary_ids=["mur_cuisine_est_1", "mur_cuisine_sud_1"],
        segment_ids=[
            "s_mur_cuisine_est_et_mur_cuisine_sud",
            "s_mur_cuisine_sud_et_mur_cuisine_est",
        ],
        id="j_mur_cuisine_est_et_mur_cuisine_sud",
    )
    house_1.link_boundaries(
        boundary_ids=[
            "mur_cuisine_sud_1",
            "mur_salon_sud_1",
            "mur_salon_cuisine",
        ],
        segment_ids=[
            "s_mur_cuisine_sud_et_mur_salon_sud",
            "s_mur_salon_sud_et_mur_cuisine_sud",
            "s_mur_salon_cuisine_et_mur_salon_sud",
        ],
        id="j_mur_cuisine_sud_et_mur_salon_sud",
    )
    house_1_dataset: Dict[str, Any] = house_1.to_dict()
    assert "simulation_parameters" in house_1_dataset["project"]
    assert "module_collection" in house_1_dataset["project"]
    assert "building_land" in house_1_dataset["project"]
    assert "node_collection" in house_1_dataset["project"]
    assert "boundary_collection" in house_1_dataset["project"]
    assert "archetype_collection" in house_1_dataset["project"]


if __name__ == "__main__":

    def test_dataset_2(monkeypatch: MonkeyPatch):
        modules: List[str] = [
            "AcvExploitationOnly",
            "LimitedGenerator",
            "OccupantModel",
            "LayerWallLosses",
            "ThermalSpaceSimplified",
            "WeatherModel",
        ]
        dataset_6: DataSet = DataSet(modules=modules, verbose=True)
        dataset_6.set_module_parameters(module_name="AcvExploitationOnly")
        print(dataset_6.module_collection)

    """
    from contextlib import contextmanager
    from unittest.mock import MagicMock

    @contextmanager
    def mock_at_level(level):
        yield

    caplog_mockup: MagicMock = MagicMock()
    caplog_mockup.at_level = MagicMock(side_effect=mock_at_level)
    caplog_mockup.text = (
        "thermal_conductivity"
        "+Thermal conductivity of the layer."
        "+format: float"
        "+unit: W/(m.K)"
        "---"
        "+List of parameters for the Layer (Archetypes) object"
        "+thickness: Thickness of the layer. [m]"
        "+thermal_conductivity: Thermal conductivity of the layer. [W/(m.K)]"
        "+List of parameters for the Space (StructureObject) object"
        "+id: Unique identifier (ID) of the space. [-]"
        "+q_needs: Needs of the space. [W]"
    )
    test_dataset(caplog=caplog_mockup, monkeypatch=MonkeyPatch())
    """
