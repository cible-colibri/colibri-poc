
root_scheme = {
    "type": "boundary object",
    "info": "A boundary is a plane surface which delimited spaces and/or exterior.\nIt has two side. It can be a fictive boundary but often represents wall, floor, roof...",
    "parameters": {
        "u_value": {
            "info": "",
            "format": None,
            "min": None,
            "max": None,
            "unit": "W/(m\u00b2.K)",
            "choices": [],
            "default": 0
        },
        "area": {
            "info": "",
            "format": None,
            "min": None,
            "max": None,
            "unit": "m\u00b2",
            "choices": [],
            "default": 0
        }
    },
    "structure": {
        "type": "boundary",
        "type_id": None,
        "label": None,
        "side_1": None,
        "side_2": None,
        "azimuth": None,
        "tilt": None,
        "area": None,
        "origin": None,
        "segments": None,
        "object_collection": []
    }
}

boundary_scheme = {
    "type": "boundary object",
    "info": "A boundary is a plane surface which delimited spaces and/or exterior.\nIt has two side. It can be a fictive boundary but often represents wall, floor, roof...",
    "parameters": {
        "u_value": {
            "info": "",
            "format": None,
            "min": None,
            "max": None,
            "unit": "W/(m\u00b2.K)",
            "choices": [],
            "default": 0
        },
        "area": {
            "info": "",
            "format": None,
            "min": None,
            "max": None,
            "unit": "m\u00b2",
            "choices": [],
            "default": 0
        }
    },
    "structure": {
        "type": "boundary",
        "type_id": None,
        "label": None,
        "side_1": None,
        "side_2": None,
        "azimuth": None,
        "tilt": None,
        "area": None,
        "origin": None,
        "segments": None,
        "object_collection": []
    }
}

colibri_models_utility_weather_Weather_scheme = {
    "constant_ground_temperature": {
        "info": "Impose a constant ground temperature if the parameter is not None",
        "format": None,
        "min": None,
        "max": None,
        "unit": "\u00b0C",
        "choices": [],
        "default": 16
    }
}

colibri_core_processing_building_building_data_BuildingData_scheme = {}

colibri_models_example_archi_wall_simplified_wall_losses_SimplifiedWallLosses_scheme = {}

colibri_models_example_archi_limited_generator_LimitedGenerator_scheme = {}

colibri_models_example_archi_thermal_space_ThermalSpaceSimplified_scheme = {}

colibri_models_example_archi_acv_exploitation_only_model_ACVExploitationOnlyModel_scheme = {}
