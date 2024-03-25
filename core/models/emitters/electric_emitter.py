import numpy as np

from core.templates.inputs import Inputs
from core.templates.outputs import Outputs
from core.templates.parameters import Parameters
from core.variables.variable import Variable
from core.models.emitters.emitter import Emitter
from utils.enums_utils import Roles, Units


class ElectricEmitter(Emitter):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        super(ElectricEmitter, self).__init__(name, inputs, outputs, parameters)

        # parameters
        self.efficiency = Variable("efficiency", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter efficiency")

        # input

        # outputs
        self.electric_load = Variable("electric_load", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="electric_load")

    def initialize(self) -> None:

        self.electric_load = 0.
        self.phi_radiative = 0.
        self.phi_convective = 0.
        self.phi_latent = 0.

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.electric_load = self.heat_demand.value * self.efficiency
        self.phi_radiative = self.heat_demand.value * self.radiative_share
        self.phi_convective = self.heat_demand.value * (1 - self.radiative_share)

    def iteration_done(self, time_step: int = 0):
        self.electric_load_last = self.electric_load


    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")


    def check_units(self) -> None:
        pass

    def calc_convergence(self, threshold=1e-3):
        self.has_converged = np.sum(np.abs(self.electric_load - self.electric_load_last)) <= threshold