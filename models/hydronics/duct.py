# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.model    import Model
from core.variable import Variable

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class Duct(Model):

    def __init__(self, name: str):
        self.name    = name
        self.inputs  = [
                             Variable("inlet_flow"),
                             Variable("inlet_temperature"),
                        ]
        self.outputs = [
                            Variable("outlet_flow"),
                            Variable("outlet_temperature"),
                        ]

    def run(self):
        self.get_output("outlet_flow").value        = self.get_input("inlet_flow").value
        self.get_output("outlet_temperature").value = self.get_input("inlet_temperature").value / 2
