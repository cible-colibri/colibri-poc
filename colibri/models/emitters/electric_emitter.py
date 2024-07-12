import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.templates.outputs import Outputs
from colibri.core.templates.parameters import Parameters
from colibri.core.variables.variable import Variable
from colibri.models.emitters.emitter import Emitter
from colibri.utils.enums_utils import Roles, Units


class ElectricEmitter(Emitter):
    def __init__(self, name: str):
        super(ElectricEmitter, self).__init__(name)

        # parameters
        self.efficiency = self.field("efficiency", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter efficiency")

        # input

        # outputs
        self.electric_load = self.field("electric_load", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="electric_load")

    def initialize(self) -> None:

        self.electric_load = 0.
        self.phi_radiative = 0.
        self.phi_convective = 0.
        self.phi_latent = 0.

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.electric_load = self.heat_demand * self.efficiency
        self.phi_radiative = self.heat_demand * self.radiative_share
        self.phi_convective = self.heat_demand * (1 - self.radiative_share)

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