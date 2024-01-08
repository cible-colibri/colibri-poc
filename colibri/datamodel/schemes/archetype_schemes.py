# -*- coding: utf-8 -*-
"""
Module that provides the schema of archetypes for each type according to the partitioning of the Colibri JDDP V1 model.
Ultimately, these schemas will result from the concatenation of the needeed parameters of each module used in the chosen Colibri assembly
(so we are waiting for the partitioning of the calculation into modules in order to achieve this functionality).
"""

# ========================================
# External imports
# ========================================

# ========================================
# Internal imports
# ========================================

# ========================================
# Constants
# ========================================

# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

# ========================================
# Functions
# ========================================

# ========================================
# Schemes
# ========================================

boundary_types_scheme = {
    "type" : "boundary archetype",
    "info" : "boundary are used to defined space delimitations, they can be wall, floor, roof, or virtual boundary (in this case 100% fill with holes). They are defined by two face and all other building element are necessary attached to a boundary",
    "parameters" :  {
        "label" : {
                       "info" : "name of the archetype type, not used as id",
                       "format" : "string",
                       "min" : None,
                       "max": None,
                       "unit" : None,
                       "choices" : None,
                       "default" : None
                   },
        "layers" : {
                       "info" : "collection of layers set by order (side 1 to side 2 of the boundary)."
                             "Layers are referenced as layer types."
                             "ex : {'type': 'layer', 'type_id' : 'id_layer_0000'}",
                       "format" : "list",
                       "min" : None,
                       "max": None,
                       "unit" : None,
                       "choices" : None,
                       "default" : None}
    },
    "structure" : {
        "label" : None,
        "layers" : [{"type":"layer", "type_id":None}]
    }
}

layer_types_scheme = {
    "type" : "layer archetype",
    "info" : "Layer as used as constitutive component of each boundary from face to face.",
    "parameters" : {
        "label" : {
                "info" : "name of the archetype type, not used as id",
                "format" : "string",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
                   },
        "thermal_conductivity" : {
                "info" : "thermal conductivity of a layer also known as lambda",
                "format" : "float",
                "min" : 0.01,
                "max": 5,
                "unit" : "W/(m.K)",
                "choices" : None,
                "default" : 1.75
            },
        "specific_heat" : {
                "info" : "specific heat capacity of a layer also known as C",
                "format" : "float",
                "min" : 100,
                "max": 8000,
                "unit" : "J/kg",
                "choices" : None,
                "default" : 0.9 #
            },
        "density" : {
                "info" : "density of a layer",
                "format" : "float",
                "min" : 0.1,
                "max": 50000,
                "unit" : "kg/m3",
                "choices" : None,
                "default" : 2500
            },
        "thickness" : {
                "info" : "thickness of a layer",
                "format" : "float",
                "min" : 0.001,
                "max": 2,
                "unit" : "m",
                "choices" : None,
                "default" : 0.3
        },
        "constitutive_materials" : {
                "info" : "collection of materials composing the layer"
                            "Material are describe by a dict composed of parameters 'share' (ratio) and 'constitutive_material_type' (enum)"
                             "ex : {'share': 0.8, 'material_type' : 'granulat'}."
                         "The sum of the share of each element of the collection as to be equal to 1"
                         "Search for constitutive_material_type and share to know more...",
                "format" : "list",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : [{'share': 1, 'material_type' : 'concrete'}]
        },
        "share" : {
                "info" : "share of a component inside a layer composition",
                "format" : "float",
                "min" : 0,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : 1
        },
        "constitutive_material_type" : {
                "info" : "type of constitutive material",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["air", "plaster", "cement", "sand", "aggregates", "cellulose wadding", "plastic", "glass wool", "wood","polystyrene","rubber", "rock wool"], #TODO : adjust, complete
                "default" : "cement"
        },
        "lca_impact_properties" : {
                "info" : "LCA impact matrix for the given fonctional unit of the layer. rows are representing each EN15804 impacts and columns impact for each LCA phase",
                         #TODO : indiquer l'ordre des lignes et colonnes comme dans UrbanPrint,
                "format" : "matrix",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None, #TODO on pourrait mettre la matrice vide mais je la mets par pour l'instant pour pas alourdir
        },
        "end_of_life_properties" : {
                "info" : "possible use of the layer at the end of its life (recyclability, waste...) by share of the layer material"
                         "ex : [{'share':0.3, 'end_of_life_properties':'re-usable'},{'share':0.7, 'end_of_life_properties':'non-reusable'}],"
                         "The sum of the share of each element of the collection as to be equal to 1"
                         "Search for end_of_life and share to know more...",
                "format" : "list",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
        },
        "end_of_life" : {
                "info" : "possible use of the share of the layer at the end of its life (recyclability, waste...)",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["re-usable", "recyclable", "non-reusable"], #TODO : adjust, complete
                "default" : "non-reusable"
        },
        "material_type": {
                "info" : "main material characterization of the layer",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["concrete", "wood", "insulation", "plaster"], #TODO : adjust, complete
                "default" : "concrete"
        },
        "light_reflectance": {
                "info" : "light reflectance of a layer in case of a use on boundary's surface also known as LRV."
                         "Measure of visible and usable light that is reflected from a surface when illuminated by a light source",
                "format" : "float",
                "min" : 0.05,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : 0.8
        },
        "albedo": {
                "info" : "light reflectance of a layer in case of a use on boundary's surface also known as LRV."
                         "Measure of solar light (visible + non visible light) that is reflected from a surface when illuminated by a light source",
                "format" : "float",
                "min" : 0,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : 0.25
        },
        "emissivity": {
                "info" : "emissitivy of a layer, compared to the reference of a perfect black body",
                "format" : "float",
                "min" : 0,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : 0.92
        },
        "installation_year": {
                "info" : "Installation year of the layer inside the boundary",
                "format" : "int",
                "min" : 1600,
                "max": 2050,
                "unit" : "year date",
                "choices" : None,
                "default" : 0.92
        },
        "service_life": {
                "info" : "Reference life of the layer",
                "format" : "int",
                "min" : 1,
                "max": 100,
                "unit" : "year",
                "choices" : None,
                "default" : 50
        }
    },
    "structure": {
        "label" : None,
        "thermal_conductivity": None,
        "specific_heat" : None,
        "density": None,
        "thickness":None,
        "constitutive_materials" : [{"share":None,"constitutive_material_type":None}],
        "lca_impact_properties" : None,
        "end_of_life_properties":None,
        "material_type":None,
        "light_reflectance":None,
        "albedo":None,
        "emissivity":None,
        "installation_year":None,
        "service_life":None,
    }
}

terminal_vent_types_scheme = {
    "type" : "terminal_vent archetype",
    "info" : "terminal vent can be air inlet, air outlet or grid.",
    "parameters" : {
        "label" : {
                "info" : "name of the archetype type, not used as id",
                "format" : "string",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
                   },
        "terminal_vent_type" : {
            "info": "type of inlet/outlet vent system : auto, hygro... The fact that it is an inlet or outlet is deducted by the nodes connexions",
            "format": "enum",
            "min": None,
            "max": None,
            "unit": None,
            "choices": ["hygro","auto","grid"], #TODO : adjust, complete
            "default": None
        },
        "relative_humidity_control" : {
            "info": "USED FOR HYGRO VENT : flow/humidity rate law of the terminal vent described as a list of flow_rate point (m3)/humidity rate (between 0 and 1)."
                    "Ex: [ {'flow_rate' : 10, 'humidity':0.55}, {'flow_rate' : 45, 'humidity':0.67}]"
                    "Search for flow_rate and humidity to know more...",
            "format": "list",
            "min": None,
            "max": None,
            "unit": None,
            "choices": None,
            "default": None
        },
        "relative_pressure_control" : {
            "info": "USED FOR AUTO VENT : flow/relative pression law of the terminal vent described as a list of flow_rate point (m3)/delta pressure (in Pa)."
                    "Ex: [ {'flow_rate' : 45, 'delta_pressure': 20}, {'flow_rate' : 45, 'delta_pressure':100}]"
                    "Search for flow_rate and delta_pressure to know more...",
            "format": "list",
            "min": None,
            "max": None,
            "unit": None,
            "choices": None,
            "default": None
        },
        "humidity": {
                "info" : "relative humidity of air",
                "format" : "float",
                "min" : 0,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : None,
        },
        "pressure": {
                "info" : "relative pressure on either side of the terminal vent",
                "format" : "float",
                "min" : 1,
                "max": 500,
                "unit" : "Pa",
                "choices" : None,
                "default" : None,
        },
        "flow_rate": {
                "info" : "flow rate through the terminal vent",
                "format" : "float",
                "min" : 0,
                "max": None,
                "unit" : "m3/h", #TODO : bonne unité ?
                "choices" : None,
                "default" : None,
        },
        "reference_pressure" : {
            "info": "USED FOR AIR INLET/GRID : reference relative pressure on either side of grid",
            "format": "float",
            "min": 1,
            "max": 500,
            "unit": "Pa",
            "choices": None,
            "default": 80,
        },
        "reference_flow_rate" : {
            "info": "USED FOR AIR INLET/GRID : reference flow rate obtained at reference pressure",
            "format": "float",
            "min": 0,
            "max": None,
            "unit": "m3/h",
            "choices": None,
            "default": 45,
        },
        "reference_temperature" : {
            "info": "reference temperature used for calculate pressure, humidity and flow rate reference parameters of the terminal vent",
            "format": "float",
            "min": 1,
            "max": 50,
            "unit": "°C",
            "choices": None,
            "default": 20,
        },
        "constitutive_materials" : {
                "info" : "collection of materials composing the terminal vent"
                            "Material are describe by a dict composed of parameters 'share' (ratio) and 'constitutive_material_type' (enum)"
                             "ex : {'share': 0.8, 'material_type' : 'granulat'}."
                         "The sum of the share of each element of the collection as to be equal to 1"
                         "Search for constitutive_material_type and share to know more...",
                "format" : "list",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : [{'share': 1, 'material_type' : 'plastic'}]
        },
        "share" : {
                "info" : "share of a component inside a terminal vent composition",
                "format" : "float",
                "min" : 0,
                "max": 1,
                "unit" : None,
                "choices" : None,
                "default" : 1
        },
        "constitutive_material_type" : {
                "info" : "type of constitutive material of a terminal vent",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["plastic","polystyrene","rubber"], #TODO : adjust, complete
                "default" : "plastic"
        },
        "end_of_life_properties" : {
                "info" : "possible use of the terminal vent components at the end of its life (recyclability, waste...) by share of the terminal vent material"
                         "ex : [{'share':0.3, 'end_of_life_properties':'re-usable'},{'share':0.7, 'end_of_life_properties':'non-reusable'}],"
                         "The sum of the share of each element of the collection as to be equal to 1"
                         "Search for end_of_life and share to know more...",
                "format" : "list",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
        },
        "end_of_life" : {
                "info" : "possible use of the share of the terminal vent at the end of its life (recyclability, waste...)",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["re-usable", "recyclable", "non-reusable"], #TODO : adjust, complete
                "default" : "non-reusable"
        },
        "service_life": {
                "info" : "Reference life of the terminal vent",
                "format" : "int",
                "min" : 1,
                "max": 100,
                "unit" : "year",
                "choices" : None,
                "default" : 50
        }

    },
    "structure" : {
            "label": None,
            "terminal_vent_type": None,
            "relative_humidity_control": None,
            "relative_pressure_control": None,
            "reference_pressure": None,
            "reference_temperature": None,
            "reference_flow_rate": None,
            "constitutive_materials": [{"share":None,"constitutive_material_type":None}],
            "lca_impact_properties" : None,
            "end_of_life_properties" : [{"share":None,"end_of_life":None}],
            "service_life" : 50,
    }

}

#TODO window and door archetype properties to complete in task force
window_types_scheme = {
    "type" : "window archetype",
    "info" : "window of the building. TODO parameters scheme : just example here",
    "parameters": {
            "label" : {
                "info" : "name of the archetype type, not used as id",
                "format" : "string",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
                   },
            "x_length" : {
                "info" : "length of the window block",
                "format" : "string",
                "min" : 0,
                "max": 30,
                "unit" : "m",
                "choices" : None,
                "default" : 0.6
                   },
            "y_length" : {
                "info" : "height of the window block",
                "format" : "string",
                "min" : 0,
                "max": 30,
                "unit" : "m",
                "choices" : None,
                "default" : 0.8
                   },

    },
    "structure" : {
        "label" : None,
        "x_length" : None,
        "y_length" : None
    }
}

door_types_scheme = {
    "type" : "door archetype",
    "info" : "TODO : Doors are not windows ?", #TODO
    "parameters": {
            "label" : {
                "info" : "name of the archetype type, not used as id",
                "format" : "string",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
                   },
            "x_length" : {
                "info" : "length of the door block",
                "format" : "string",
                "min" : 0,
                "max": 30,
                "unit" : "m",
                "choices" : None,
                "default" : 0.6
                   },
            "y_length" : {
                "info" : "height of the door block",
                "format" : "string",
                "min" : 0,
                "max": 30,
                "unit" : "m",
                "choices" : None,
                "default" : 0.8
                   },

    },
    "structure" : {
        "label" : None,
        "x_length" : None,
        "y_length" : None
    }
}