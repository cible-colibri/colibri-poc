# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import dataclasses

# ========================================
# Internal imports
# ========================================

from utils.enums_utils import Units

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

@dataclasses.dataclass
class Variable:
    name: str
    value: float = 0
    unit: Units = Units.UNITLESS
    description: str = "Sorry, no description yet."

# ========================================
# Functions
# ========================================
