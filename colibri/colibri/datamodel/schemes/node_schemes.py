# -*- coding: utf-8 -*-
"""
Module that provides the schema for each node element of the building (space, linear_junction...).
The COLIBRI data model always retains these schemas.
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


#region Nodes schemas
#TODO : QUESTION : est ce qu'on se permet de factoriser des propriétés dans les archetypes (genre le psi des linear junction) ?
space_scheme = {
    "type" : "space node",
    "info" : "A space is a continuous volume delimited by boundaries",
    "parameters" : {
        "label" : {
            "info" : "name of the space, not used as id",
            "format" : "string",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
                   },
        "reference_area": {
            "info": "reference area of the space (could be floor area, shab, useful area...)",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "m²",
            "choices" : None,
            "default" : None
        },
        "volume": {
            "info": "total volume of the space",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "m3",
            "choices" : None,
            "default" : None
        },
        "altitude": {
            "info": "altitude of the lowest point in space (0 : sea level)",
            "format" : "float",
            "min" : 0,
            "max": 8849,
            "unit" : "m",
            "choices" : None,
            "default" : 0
        },
        "use" : {
                "info" : "Main typology use of the space",
                "format" : "enum",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : ["bedroom", "living room", "kitchen", "office", "bathroom", "storage", "garage", "attic", "circulation", "other"], #TODO : adjust, complete
                "default" : "living room"
        },
        "air_permeability": {
            "info": "air permeability of the space under 4Pa pressure difference. It represents the leak rate relative to the surface of the space boundary in contact with the exterior.",
            "format" : "float",
            "min" : 0,
            "max": 4,
            "unit" : "m3/(h.m2)",
            "choices" : None,
            "default" : 1.3
        },
    },
    "structure" : {
            "label" : None,
            "node_type": "space",
            "volume": None,
            "reference_area": None,
            "altitude": None,
            "use": None,
            "air_permeability": None}

}

ponctual_junction_scheme = {
    "type" : "ponctual_junction node",
    "info" : "A ponctual junction is used when objects are link through an assimilated 'single point connexion'"
             "\n Example : a pipes with an air vent.",
    "parameters" : {
        "altitude": {
            "info": "absolute altitude at which the ponctual junction is made",
            "format" : "float",
            "min" : 0,
            "max": 8849,
            "unit" : "m",
            "choices" : None,
            "default" : 0
        },
        "binding_mode": {
            "info": "describe the way the connexion is made between the two object."
                    "\nCan be used as information for circular economy calculation for example",
            "format" : "enum",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : ["virtual", "nut", "welding"], #TODO : transform adjust
            "default" : "virtual"
        },

    },
    "structure" : {
        "node_type" : "ponctual_junction",
        "altitude" : None,
        "binding_mode" : None
    }
}

linear_junction_scheme = {
    "type" : "linear_junction node",
    "info" : "A linear junction is used when boundaries are in contact on a segment."
             "\n It can be used for thermal bridges calculation for example and also to understand the 3D structure of the project",
    "parameters" : {
        "length": {
            "info": "Lenght of contact between the boundaries",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "m",
            "choices" : None,
            "default" : None
        },
        "psi": {
            "info": "linear thermal transmission coefficient used for express thermal bridges associated with the junction",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "W/(K.m)",
            "choices" : None,
            "default" : 0.5
        },
        "binding_mode": {
            "info": "describe the way the connexion is made between the two boundaries."
                    "\nCan be used as information for circular economy calculation for example",
            "format" : "enum",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : ["virtual", "chemical","mechanical"], #TODO : transform adjust
            "default" : "virtual"
        },

    },
    "structure" : {
        "node_type" : "linear_junction",
        "binding_mode" : None,
        "psi" : None,
        "length" : None
    }
}

#TODO : manque boundary condition à créer

#endregion
