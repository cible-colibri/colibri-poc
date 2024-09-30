"""
Constants for the `colibri` package.
"""

import logging

from colibri.utils.logging_utils import initialize_logger
from colibri.utils.units_utils import UnitConverter, get_unit_converter

# Logger to print info, debug, warning, error, etc.
LOGGER: logging.Logger = initialize_logger()
# Object to convert from one unit to another (has all unit conversion factors)
UNIT_CONVERTER: UnitConverter = get_unit_converter()

# Internal variable names
ATTACHED_TO: str = "attached_to"
ARCHETYPES: str = "archetypes"
ARCHETYPE_COLLECTION: str = "archetype_collection"
BUILDING_COLLECTION: str = "building_collection"
BOUNDARY: str = "boundary"
BOUNDARY_COLLECTION: str = "boundary_collection"
CATEGORY: str = "category"
COLIBRI: str = "colibri"
COLIBRI_INTERFACES_MODULE_PATH: str = "colibri.interfaces"
COLIBRI_MODULES_MODULE_PATH: str = "colibri.modules"
COLIBRI_PROJECT_OBJECTS_MODULE_PATH: str = "colibri.project_objects"
COLLECTION: str = "collection"
DEFAULT: str = "default"
DESCRIPTION: str = "description"
ELEMENT_OBJECT: str = "ElementObject"
ENUM: str = "enum"
FORMAT: str = "format"
FORWARD_REF: str = "ForwardRef"
INPUTS: str = "inputs"
JUNCTION: str = "junction"
LINEAR_JUNCTION: str = "linear_junction"
MAX: str = "max"
MIN: str = "min"
MODULE: str = "module"
MODULE_COLLECTION: str = "module_collection"
NODE_COLLECTION: str = "node_collection"
OUTPUTS: str = "outputs"
PARAMETERS: str = "parameters"
PROJECT: str = "project"
PROJECT_DATA: str = "ProjectData"
PUNCTUAL_JUNCTION: str = "PunctualJunction"
OBJECT_COLLECTION: str = "object_collection"
REQUIRED: str = "required"
SPACE: str = "Space"
SEGMENT: str = "segment"
SEGMENTS: str = "segments"
SERIES_EXTENSION_NAME: str = "_series"
SIMULATION_PARAMETERS: str = "simulation_parameters"
SLOTS: str = "__slots__"
SPACE_COLLECTION: str = "space_collection"
TYPE: str = "type"
TYPING: str = "typing"
TYPE_ID: str = "type_id"
UNIT: str = "unit"
