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

class Link:
    from_model: Model = None
    to_model: Model = None
    from_variable: str = None
    to_variable: str = None

    def __init__(self, *args):
        if len(args) == 4:
            self.from_model = args[0]
            self.from_variable = args[1]
            self.to_model = args[2]
            self.to_variable = args[3]
        else:
            self.from_model = None
            self.to_model = None
            self.from_variable = None
            self.to_variable = None


# ========================================
# Functions
# ========================================
