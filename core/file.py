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
class File:
    name: str
    path: str
    description: str = ""

    def __init__(self, name: str, path: str, description : str = ""):
        self.name    = name
        self.path    = path
        self.description = description

# ========================================
# Functions
# ========================================
