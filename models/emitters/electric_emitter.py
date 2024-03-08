import numpy as np

from core.inputs import Inputs
from core.model import Model
from core.outputs import Outputs
from core.parameters import Parameters
from core.variable import Variable
from utils.enums_utils import Roles, Units


class ElectricEmitter(Model):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        # self.case = Variable("case", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="The building to use")
        self.zone_name = Variable("zone_name", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="zone_name")
        self.efficiency = Variable("efficiency", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter efficiency")
        self.radiative_share = Variable("radiative_share", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="radiative_share")
        self.time_constant = Variable("time_constant", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter time constant")
        self.nominal_heating_power = Variable("nominal_heating_power", 0, role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal heating power")
        self.nominal_cooling_power = Variable("nominal_cooling_power", 0, role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal cooling power")

        # input
        self.heat_demand = Variable("heat_demand", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="heat_demand - positive=heating, negative=cooling")

        # results to save
        self.phi_radiative = Variable("phi_radiative", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Radiative part of thermal output")
        self.phi_convective = Variable("phi_convective", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Convective part of thermal output")
        self.phi_latent = Variable("phi_latent", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Latent part of thermal output")
        self.electric_load = Variable("electric_load", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="electric_load")

    def initialize(self) -> None:
        self.nominal_heating_power = 10000.
        self.nominal_cooling_power = 10000.

        self.electric_load = 0.
        self.phi_radiative = 0.
        self.phi_convective = 0.
        self.phi_latent = 0.

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.electric_load = self.heat_demand.value * self.efficiency
        self.phi_radiative = self.heat_demand.value * self.radiative_share
        self.phi_convective = self.heat_demand.value * (1 - self.radiative_share)

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        return True #self.has_converged

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