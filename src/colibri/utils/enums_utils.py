"""
Enumerations for the `colibri` package.
"""

from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class ProjectObjectCategories:
    name: str
    path: str


@unique
class ColibriProjectObjects(Enum):
    ARCHETYPE = "Archetype"
    BOUNDARY = "Boundary"
    BOUNDARY_OBJECT = "BoundaryObject"
    ELEMENT_OBJECT = "ElementObject"
    PROJECT = "Project"
    SPACE = "Space"


@unique
class ColibriProjectPaths(Enum):
    ARCHETYPE = ProjectObjectCategories(
        ColibriProjectObjects.ARCHETYPE, "project.archetype_collection"
    )
    BOUNDARY = ProjectObjectCategories(
        ColibriProjectObjects.BOUNDARY, "project.boundary_collection"
    )
    BOUNDARY_OBJECT = ProjectObjectCategories(
        ColibriProjectObjects.BOUNDARY_OBJECT,
        "project.boundary_collection.Boundary.object_collection",
    )
    ELEMENT_OBJECT = ProjectObjectCategories(
        ColibriProjectObjects.ELEMENT_OBJECT, "."
    )
    PROJECT = ProjectObjectCategories(ColibriProjectObjects.PROJECT, "project")
    SPACE = ProjectObjectCategories(
        ColibriProjectObjects.SPACE, "project.node_collection.space_collection"
    )

    def get_path_from_object_type(object_type):
        paths = [
            oc.value.path
            for oc in ColibriProjectPaths
            if oc.value.name.value == object_type
        ]
        if len(paths) == 1:
            return paths[0]
        return None


# TODO : unify with ColibriCategories in dataset.py


@unique
class ColibriCategories(Enum):
    ARCHETYPE = "archetype"
    PROJECT_OBJECT = "project_object"


@unique
class ColibriObjectTypes(Enum):
    MODULE = "module"
    PROJECT_OBJECT = "project_object"


@unique
class ErrorMessages(Enum):
    ATTACHMENT_ERROR = "Attachment error."
    COLIBRI_MODULE_NOT_FOUND_ERROR = "Colibri module not found."
    INITIALIZATION_ERROR = "Colibri project could not be initialized."
    LINK_ERROR = "Link error."
    UNAUTHORIZED_COLIBRI_MODULE_ERROR = "Colibri module not authorized."
    UNIT_ERROR = "Unit error."
    USER_INPUT_ERROR = "Input not valid."


@unique
class Roles(Enum):
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    PARAMETERS = "parameters"


@unique
class Units(Enum):
    CENTIMETER = "cm"
    CO2_KILO_GRAM_EQUIVALENT = "kgCO2"
    CO2_KILO_GRAM_EQUIVALENT_PER_KILO_WATT_HOUR = "kgCO2/kWh"
    CUBIC_METER = "m³"
    CUBIC_METER_PER_HOUR = "m³/h"
    DEGREE = "°"
    DEGREE_CELSIUS = "°C"
    DEGREE_CELSIUS_PER_METER = "°C/m"
    DEGREE_FAHRENHEIT = "°F"
    HOUR = "h"
    JOULE = "J"
    JOULE_PER_KILO_GRAM = "J/kg"
    JOULE_PER_GRAM_PER_DEGREE_CELSIUS = "J/(g.°C)"
    JOULE_PER_KILO_GRAM_PER_DEGREE_CELSIUS = "J/(kg.°C)"
    JOULE_PER_CUBIC_METER_PER_DEGREE_CELSIUS = "J/(m³.°C)"
    KELVIN = "K"
    KILO_GRAM = "kg"
    KILO_JOULE = "kJ"
    KILO_JOULE_PER_HOUR = "kJ/h"
    KILO_METER = "km"
    KILO_WATT = "kW"
    KILO_WATT_HOUR = "kWh"
    KILOGRAM_PER_CUBIC_METER = "kg/m³"
    KILOGRAM_PER_HOUR = "kg/h"
    KILOGRAM_PER_SECOND = "kg/s"
    METER = "m"
    PASCAL = "Pa"
    SECOND = "s"
    SQUARE_METER = "m²"
    UNITLESS = "-"
    YEAR = "year"
    WATT = "W"
    WATT_HOUR = "Wh"
    WATT_PER_KELVIN = "W/K"
    WATT_PER_SQUARE_METER = "W/m²"
    WATT_PER_METER_PER_KELVIN = "W/(m.K)"
    WATT_PER_SQUARE_METER_PER_KELVIN = "W/(m².K)"
    WATT_PER_SQUARE_METER_PER_SQUARE_KELVIN = "W/(m².K²)"
