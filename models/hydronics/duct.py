# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================
from math import exp

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
            Variable("loss_coefficient", 3.0), # kJ/h
            Variable("cp_fluid", 4.186), #  J/g°C
            Variable("inlet_flow_rate", 100), # kg/h
            Variable("inlet_temperature", 40), # °C
            Variable("outside_temperature", 20) # °C
        ]
        self.outputs = [
                            Variable("outlet_flow_rate"), # kg/h
                            Variable("outlet_temperature"), # °C
                        ]
    def initialize(self):
        self.loss_factor = 1. - exp(- self.loss_coefficient / (self.inlet_flow_rate * self.cp_fluid))

    def run(self):
        self.outlet_flow_rate = self.inlet_flow_rate
        self.outlet_temperature = (1. - self.loss_factor) * self.inlet_temperature + self.loss_factor * self.outside_temperature
        pass

    def simulation_done(self):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")
