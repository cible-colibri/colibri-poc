import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class LayerWallLossesNoLoop(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name

        self.Text = Variable("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Tint = Variable("Tint", 20.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)

        self.QWall_out = Variable("QWall_out", 0.0, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

        self.e = Variable("e", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="épaisseurs des couches")
        self.Lambda = Variable("Lambda", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="conductivité de la couche")
        self.S = Variable("Surface", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="surface")

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.U = []
        for e1, L1 in zip(self.e.value, self.Lambda.value):
            R = sum([e11 / L11 for e11, L11 in zip(e1, L1)])
            self.U.append(1 / R)

        self.Qwall = np.array(self.U) * np.array(self.S.value) * (np.array(self.Tint.value) - np.array(self.Text.value))


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









