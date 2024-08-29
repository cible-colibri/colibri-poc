import typing

# ========================================
# Internal imports
# ========================================

from colibri.utils.enums_utils import (
                                Roles,
                                Units,
                               )

# ========================================
# Constants
# ========================================

from colibri.config.constants import UNIT_CONVERTER


SelfField          = typing.TypeVar("SelfField", bound = "Field")

class Field:

    def __init__(self, name: str, default_value: typing.Any, role: Roles, unit: Units = Units.UNITLESS, format = None, min = None, max = None, description: str = "", model = None, structure = [], check_convergence: bool = False, n_max_iterations = 10, key=None, choices = []):
        self.name = name
        self.default_value = default_value
        self.role = role
        self.unit = unit
        self.format = format
        self.min = min
        self.max = max
        self.description = description
        self.model = model
        self.structure = structure
        self.check_convergence = check_convergence
        self.convergence_tolerance = 0.1
        self.n_max_iterations = n_max_iterations
        self.key=key
        self.choices = choices

    def get_scheme(self):
        return {
            'info': self.description,
            "format": self.format,
            "min": self.min,
            "max": self.max,
            "unit": self.unit,
            "choices": self.choices,
            "default": self.default_value
        }

    def convert(self, target_unit: Units) -> float:
        return UNIT_CONVERTER.convert(self, self.unit, target_unit)
