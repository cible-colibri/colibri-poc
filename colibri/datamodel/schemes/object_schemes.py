# -*- coding: utf-8 -*-
"""
Module that provides the schema for each building object (global structure, boundary description, etc.).
These schemas are independent of the choice of calculation modules (parameters) but determine the geometrical and topological descriptions
of building elements. Therefore, the COLIBRI data model always retains these schemas.
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

#region Global structure of a COLIBRI dataset
root_scheme = {
    "type" : "global structure",
    "info" : "global structure of a COLIBRI json",
    "parameters" : {},
    "structure" : {
        "building_land" : {},
        "nodes_collection" : {},
        "boundary_collection" : {},
        "archetype_collection" : {},
    }

}


#endregion

#region Schema of an individual boundary inside boundary_collection
boundary_scheme = {
    "type" : "boundary object",
    "info" : "A boundary is a plane surface which delimited spaces and/or exterior."
             "\nIt has two side. It can be a fictive boundary but often represents wall, floor, roof...",
    "parameters" : {
        "label" : {
            "info" : "name of the boundary (wall), not used as id",
            "format" : "string",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
                   },
        "side_1": {
            "info": "identifier of the space (or 'exterior' or 'ground' if not connected to a space or a bundary_condition node) onto which face 1 of the boundary is in contact",
            "format" : "string",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
                   },
        "side_2": {
                "info": "identifier of the space (or 'exterior' if not connected to a space) onto which face 1 of the boundary is in contact",
                "format" : "string",
                "min" : None,
                "max": None,
                "unit" : None,
                "choices" : None,
                "default" : None
                    },
        "azimuth": {
            "info": "normal orientation of the side 1 of the boundary",
            "format" : "int",
            "min" : 0,
            "max": 359,
            "unit" : "°",
            "choices" : None,
            "default" : None
        },
        "tilt": {
            "info": "inclination of the boundary inclination of the wall relative to the horizontal"
                    "0° : horizontal facing upwards, 90° : vertical, 180° : horizontal facing downwards",
            "format" : "int",
            "min" : 0,
            "max": 180,
            "unit" : "°",
            "choices" : None,
            "default" : None
        },
        "area": {
            "info": "total area of the boundary in the middle of the wall" #TODO : attention a voir si il faut side_1_area, side_2_area ou pas ou si on laisse les moteur recalculés
                    "including the surface occupied by elements such as windows (gross area of the boundary)",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "m²",
            "choices" : None,
            "default" : None
        },
        "3d_origin": {
            "info": "Origin (x,y,z) in the absolute reference of the first point of the first segment of the boundary"
                    "Can be used to build the 3d model without using segment information for rebuild anything", #TODO create a function that create that automatically
            "format" : "tuple",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
        },
        "segments": {
            "info": "Collection of segment forming the edges of the boundary or in case of a non 3D description linears of interest for modeling."
                    "Important : coordinates needs to be set in CLOCKWISE order regarding side_1 of the boundary"
                    "The coordinates of segments are set in a 2D plane (boundaries are always planar) with a relative reference point, where the first point of the boundary is designated as x:0, y:0."
                    "In case of a non use of 3D, 'points' key is set to None and only 'length' is used."
                    "Examples :[ {'id' : 'arrete_1'', 'points' : [[x1,y1],[x2,y2]], 'length' : 10, 'junction' : {'nodes_type' : 'linear_junction','nodes_id' : 'junction_64'} ]"
                    "Search for 'points', 'length', 'junction' to know more...",
            "format" : "list",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
        },
        "element_collection" : {
            "info": "Collection of element linked to the boundary (windows, doors, inlet...)",
            "format" : "list",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : []
        },
        "length" : {
            "info": "length of a given segment of the boundary",
            "format" : "float",
            "min" : 0,
            "max": None,
            "unit" : "m",
            "choices" : None,
            "default" : None
        },
        "points": {
            "info": "list of the two (x,y) points coordinates forming a segment"
                    "ex : [[x1,y1], [x2,y2]]",
            "format" : "list",
            "min" : None,
            "max": None,
            "unit" : "Each coordinates use meter unit",
            "choices" : None,
            "default" : None
        },
        "junction" : {
            "info": "junction is a way to connect one segment to another using 'nodes_type' et 'nodes_id' in order to find the nodes into nodes_collection of the project. It allows multiple boundary to be on contact"
                    "ex : {'nodes_type' : 'linear_junction','nodes_id' : 'junction_64'}",
            "format" : "dict",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None
        },
    },
    "structure" : {
        "type" : "boundary",
        "type_id" : None,
        "label" : None,
        "side_1": None,
        "side_2": None,
        "azimuth" : None,
        "tilt" : None,
        "area" : None,
        "origin" : None,
        "segments" : None, #if None we know that 2d/3d geometry is not used.
        "object_collection" : []
    }

}

#endregion

#region Generic boundary object schemes
#use for window, air_vent, various objects...
#COMMENT : in very particular case of an object like a window who is not installated parallel to the boundary,
# this needs to be adress in archetype with for example "additionnal orientation/additionnal tilt"

boundary_object_scheme = {
    "type" : "generic object",
    "info" : "this scheme represents the generic scheme for all object connected to a boundary through the associated boundary key 'object_collection'\n"
             "Each object has the same generic scheme and the list key 'junction' that allows to create other type of node connexion between dataset elements ",
    "parameters" : {
        "x_relative_position":{
            "info": "relative x position of the object on the side (plane referential) of the boundary",
            "format" : "float",
            "min" : None,
            "max": None,
            "unit" : "m",
            "choices" : None,
            "default" : None,
        },
        "y_relative_position":{
            "info": "relative y position of the object on the affected side (plane referential) of the boundary",
            "format" : "float",
            "min" : None,
            "max": None,
            "unit" : "m",
            "choices" : None,
            "default" : None,
        },
        "z_relative_position":{
            "info": "relative z-depth position of the object compared to the affected side (plane referential) of the boundary."
                    "\nBy default 0 but can be used when something is not really exactly on one of the two side of the boundary",
            "format" : "float",
            "min" : None,
            "max": None,
            "unit" : "m",
            "choices" : None,
            "default" : 0,
        },
        "on_side" : {
            "info": "Parameter that allows to specify on which side of the boundary the object is located :"
                    "\n- 'side_1',"
                    "\n- 'side_2',"
                    "\n- 'side_1_to_side_2' : in this case the element is connected to both face and make a hole/tunnel between them (for example : a hole, a window). The direction of integration of the object is from side 1 to side 2,"
                    "\n- 'side_2_to_side_1' : in this case the element is connected to both face and make a hole/tunnel between them (for example : a hole, a window). The direction of integration of the object is from side 2 to side 1,",
            "format" : "enum",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : ["side_1","side_2","side_1_to_side_2","side_2_to_side_1"],
            "default" : None
        },
        "type" : {
            "info": "type of the object (example window) according to archetype type list",
            "format" : "str",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None,
                  },
        "type_id" : {
            "info": "id of the associated archetype object which store intrinsic properties",
            "format" : "str",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None,
                  },
        "id" : {
            "info": "unique id of object",
            "format" : "str",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : None,
                  },
        "junctions" : {
            "info": "list of node junction to which the object is connected"
                    "example format of each element of the connexion : {'nodes_type' : 'linear_junction','nodes_id' : 'junction_64'}",
            "format" : "list",
            "min" : None,
            "max": None,
            "unit" : None,
            "choices" : None,
            "default" : [],
                  },
    },
    "structure" : {
        "id" : None,
        "type" : None,
        "type_id" : None,
        "on_side" : None, #[side1, side2] through
        "x_relative_position" : None,
        "y_relative_position" : None,
        "z_relative_position" : None,
        "junctions" : []
    }
}



#endregion