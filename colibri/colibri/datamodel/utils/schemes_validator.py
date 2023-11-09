# -*- coding: utf-8 -*-
"""
Module which ensures that the different schemes (archetype, node, object respect the correct format)
"""

# ========================================
# External imports
# ========================================

from jsonschema import validate
from jsonschema.exceptions import ValidationError

# ========================================
# Internal imports
# ========================================

from colibri.datamodel.schemes import object_schemes
from colibri.datamodel.schemes import archetype_schemes, node_schemes


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

def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print("JSON is valid.")
    except ValidationError as ve:
        print("JSON is invalid.")
        raise ve

# ========================================
# Schemes
# ========================================

json_scheme_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Schema validation for an object COLIBRI",
    "description": "Schema validation for an object COLIBRI",
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "description": "Type name"
        },
        "info": {
            "type": "string",
            "description": "About the object"
        },
        "parameters": {
            "type": "object",
            "description": "List of parameters and their properties - parameters documentation"
        },
        "structure": {
            "type": "object",
            "description": "Structure of the object in the dataset"
        }
    },
    "required": ["type", "info", "parameters", "structure"],
    "additionalProperties": False
}


list_object_scheme = [name for name in dir(object_schemes) if name.endswith('_scheme')]
list_archetype_scheme = [name for name in dir(archetype_schemes) if name.endswith('_scheme')]
list_node_scheme = [name for name in dir(node_schemes) if name.endswith('_scheme')]

for json_scheme in list_object_scheme:
    object_json = getattr(object_schemes, json_scheme)
    try:
        validate(instance=object_json, schema=json_scheme_schema)
    except ValidationError as ve:
        raise ValueError(f"{json_scheme} does not respect COLIBRI object scheme schema in object_schemes.py. Please fix it according to json schema in schemes/schemes_validator.py : {ve}")

for json_scheme in list_archetype_scheme:
    object_json = getattr(archetype_schemes, json_scheme)
    try:
        validate(instance=object_json, schema=json_scheme_schema)
    except ValidationError as ve:
        raise ValueError(f"{json_scheme} does not respect COLIBRI archetype scheme schema in archetype_schemes.py. Please fix it according to json schema in schemes/schemes_validator.py : {ve}")

for json_scheme in list_node_scheme:
    object_json = getattr(node_schemes, json_scheme)
    try:
        validate(instance=object_json, schema=json_scheme_schema)
    except ValidationError as ve:
        raise ValueError(f"{json_scheme} does not respect COLIBRI node scheme schema in node_schemes.py. Please fix it according to json schema in schemes/schemes_validator.py : {ve}")
