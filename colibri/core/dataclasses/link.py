# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import dataclasses

# ========================================
# Internal imports
# ========================================

from colibri.core.model import Model

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
    index_from: int = None # zero-based index if source of link is a vector
    index_to: int = None # zero-based index if target of link is a vector

# ========================================
# Functions
# ========================================
