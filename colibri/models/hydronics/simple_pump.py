# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================


from colibri.core.model        import Model



from colibri.utils.enums_utils import (
                                Roles,
                                Units,
                               )


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

        self.name= name

        self.inlet_flow_rate = self.field("inlet_flow_rate", 100, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_temperature = self.field("inlet_temperature", 40, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_pressure = self.field("outlet_pressure", 0, role=Roles.OUTPUTS, unit=Units.PASCAL)
        self.outlet_flow_rate = self.field("outlet_flow_rate", 0, role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_temperature = self.field("outlet_temperature", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)

    def initialize(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.outlet_flow_rate = self.inlet_flow_rate
        self.outlet_temperature = self.inlet_temperature
        self.outlet_pressure = 42

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

# ========================================
# Functions
# ========================================
