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

from colibri.core.constants import UNIT_CONVERTER


SelfField          = typing.TypeVar("SelfField", bound = "Field")

class Field:

    def __init__(self, name: str, default_value: typing.Any, role: Roles, unit: Units = Units.UNITLESS, description: str = "", linked_to: typing.List[SelfField] = None, model = None, structure = []):
        self.name = name
        self.default_value = default_value
        self.role = role
        self.unit = unit
        self.description = description
        self.linked_to = linked_to
        self.model = model
        self.structure = structure

    def convert(self, target_unit: Units) -> float:
        return UNIT_CONVERTER.convert(self, self.unit, target_unit)
