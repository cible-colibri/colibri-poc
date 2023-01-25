# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

from scipy.interpolate import interp1d

# ========================================
# Internal imports
# ========================================

from core.conditions   import Conditions
from core.model        import Model
from core.parameters   import Parameters
from core.variable     import Variable
from utils.enums_utils  import Units

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class SimplePump(Model):

    def __init__(self, name: str):

        self.name       = name
        self.inputs  = [
            Variable("inlet_flow_rate", 100), # kg/h
            Variable("inlet_temperature", 40), # °C
        ]
        self.outputs = [
                            Variable("outlet_flow_rate"), # kg/h
                            Variable("outlet_temperature"), # °C
                            Variable("outlet_pressure")  # Pa
        ]

    def run(self) -> None:
        self.outlet_flow_rate = self.inlet_flow_rate
        self.outlet_temperature = self.inlet_temperature
        self.outlet_pressure = 42

