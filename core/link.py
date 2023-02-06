# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import dataclasses

# ========================================
# Internal imports
# ========================================

from core.model import Model

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
class Link:

    from_model: Model = None
    from_variable: str = None
    to_model: Model = None
    to_variable: str = None

# ========================================
# Functions
# ========================================
