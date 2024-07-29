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

    def __init__(self, name: str, default_value: typing.Any, role: Roles, unit: Units = Units.UNITLESS, description: str = "", linked_to: typing.List[SelfField] = None, model = None, structure = [], check_convergence: bool = True):
        self.name = name
        self.default_value = default_value
        self.role = role
        self.unit = unit
        self.description = description
        self.linked_to = linked_to
        self.model = model
        self.structure = structure
        self.check_convergence = check_convergence
        self.convergence_tolerance = 0.1



    def convert(self, target_unit: Units) -> float:
        return UNIT_CONVERTER.convert(self, self.unit, target_unit)
