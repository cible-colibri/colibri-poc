"""
Test for the `project_data.py` module.
"""

from colibri.core import ProjectData


def test_project_data() -> None:
    """Test the ProjectData class."""
    data: dict = {
        "project": {
            "building_land": {},
            "node_collection": {
                "space_collection": {
                    "living_room_1": {
                        "type": "space",
                        "type_id": "generic_space",
                        "label": "salon",
                        "node_type": "space",
                        "volume": 52.25,
                        "reference_area": 20.9,
                        "altitude": 0,
                        "use": "living room",
                        "air_permeability": 1.3,
                    },
                },
                "linear_junction_collection": {
                    "j_mur_salon_sud_et_mur_salon_ouest": {
                        "node_type": "linear_junction",
                        "binding_mode": "virtual",
                        "psi": 0.5,
                        "length": 2.5,
                    },
                },
            },
            "boundary_collection": {
                "mur_salon_sud_1": {
                    "id": "mur_salon_sud_1",
                    "type": "boundary",
                    "type_id": "mur_exterieur_1",
                    "label": "Mur salon sud",
                    "side_1": "exterior",
                    "side_2": "living_room_1",
                    "azimuth": 180,
                    "tilt": 90,
                    "area": 15.0,
                    "origin": None,
                    "segments": [
                        {
                            "id": "s_mur_salon_sud_et_mur_salon_ouest",
                            "points": [[0, 0], [0, 2.5]],
                            "junction": {
                                "type": "linear_junction",
                                "type_id": "j_mur_salon_sud_et_mur_salon_ouest",
                            },
                            "length": 2.5,
                        },
                    ],
                    "object_collection": [
                        {
                            "id": "door_1",
                            "type": "door",
                            "type_id": "typical_door",
                            "on_side": "side_1_to_side_2",
                            "x_relative_position": 0.6,
                            "y_relative_position": 0,
                            "z_relative_position": 0,
                            "junctions": [],
                        },
                        {
                            "id": "emitter_1",
                            "type": "emitter",
                            "type_id": "electric_convector",
                            "on_side": "side_1_to_side_2",
                            "x_relative_position": 1,
                            "y_relative_position": 1,
                            "z_relative_position": 0,
                            "junctions": [],
                        },
                    ],
                },
            },
            "archetype_collection": {
                "layer_types": {
                    "beton_1": {
                        "label": "béton 20cm",
                        "thermal_conductivity": 1.75,
                        "specific_heat": 900,
                        "density": 2500,
                        "thickness": 0.2,
                        "constitutive_materials": [
                            {
                                "share": 1,
                                "constitutive_material_type": "cement",
                            },
                        ],
                        "lca_impact_properties": None,
                        "end_of_life_properties": None,
                        "material_type": "concrete",
                        "light_reflectance": 0.8,
                        "albedo": 0.25,
                        "emissivity": 0.92,
                        "installation_year": 0.92,
                        "service_life": 50,
                    },
                },
                "boundary_types": {
                    "mur_exterieur_1": {
                        "label": "Mur exterieur",
                        "layers": [
                            {"type": "layer", "type_id": "beton_1"},
                        ],
                    },
                },
                "door_types": {
                    "typical_door": {
                        "label": "porte classique",
                        "x_length": 0.6,
                        "y_length": 0.8,
                    },
                },
                "emitter_types": {
                    "electric_convector": {
                        "label": "electric convector standard",
                        "emitter_type": "electric",
                        "efficiency": 0.3,
                        "pn": 150,
                        "radiative_share": 0.5,
                        "time_constant": 3600,
                        "nominal_heating_power": 10000,
                        "nominal_cooling_power": 10000,
                        "mode": "heating",
                        "space_coverage": 1.0,
                    }
                },
            },
        },
    }
    project_data: ProjectData = ProjectData(name="project_data", data=data)
    object_data: dict = {
        "type": "boundary",
        "type_id": "mur_exterieur_1",
        "label": "Mur salon sud",
        "side_1": "exterior",
        "side_2": "living_room_1",
        "azimuth": 180,
        "tilt": 90,
        "area": 15.0,
        "origin": None,
        "segments": [
            {
                "id": "s_mur_salon_sud_et_mur_salon_ouest",
                "points": [[0, 0], [0, 2.5]],
                "junction": {
                    "nodes_type": "linear_junction",
                    "nodes_id": "j_mur_salon_sud_et_mur_salon_ouest",
                },
                "length": 2.5,
            },
        ],
        "object_collection": [
            {
                "id": "door_1",
                "type": "door",
                "type_id": "typical_door",
                "on_side": "side_1_to_side_2",
                "x_relative_position": 0.6,
                "y_relative_position": 0,
                "z_relative_position": 0,
                "junctions": [],
            },
            {
                "id": "emitter_1",
                "type": "emitter",
                "type_id": "electric_convector",
                "on_side": "side_1_to_side_2",
                "x_relative_position": 1,
                "y_relative_position": 1,
                "z_relative_position": 0,
                "junctions": [],
            },
        ],
    }
    assert project_data.get_archetype_data(object_data=object_data) == {
        "label": "Mur exterieur",
        "layers": [{"type": "layer", "type_id": "beton_1"}],
    }
    object_data: dict = {
        "type_id": "mur_exterieur_1",
    }
    assert project_data.get_archetype_data(object_data=object_data) == dict()


if __name__ == "__main__":
    test_project_data()
