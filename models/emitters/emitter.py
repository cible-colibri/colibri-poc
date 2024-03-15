import abc

import numpy as np

from core.inputs import Inputs
from core.model import Model
from core.outputs import Outputs
from core.parameters import Parameters
from core.variable import Variable
from utils.enums_utils import Roles, Units


class Emitter(Model):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                  = name
        self.project               = None
        self.inputs                = [] if inputs is None else inputs.to_list()
        self.outputs               = [] if outputs is None else outputs.to_list()
        self.parameters            = [] if parameters is None else parameters.to_list()

        self.zone_name = Variable("zone_name", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="zone_name")
        self.radiative_share = Variable("radiative_share", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="radiative_share")
        self.nominal_heating_power = Variable("nominal_heating_power", 0, role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal heating power")
        self.nominal_cooling_power = Variable("nominal_cooling_power", 0, role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal cooling power")
        self.time_constant = Variable("time_constant", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter time constant")

        # inputs
        self.heat_demand = Variable("heat_demand", np.array(()), role=Roles.INPUTS, unit=Units.UNITLESS, description="heat_demand - positive=heating, negative=cooling")

        # outputs
        self.phi_radiative = Variable("phi_radiative", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Radiative part of thermal output")
        self.phi_convective = Variable("phi_convective", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Convective part of thermal output")
        self.phi_latent = Variable("phi_latent", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Latent part of thermal output")



    @abc.abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        raise NotImplementedError("Not implemented")


    @abc.abstractmethod
    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def iteration_done(self, time_step: int = 0):
        raise NotImplementedError("Not implemented")


    @abc.abstractmethod
    def timestep_done(self, time_step: int = 0):
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def simulation_done(self, time_step: int = 0):
        raise NotImplementedError("Not implemented")


    @abc.abstractmethod
    def check_units(self) -> None:
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def calc_convergence(self, threshold=1e-3):
        raise NotImplementedError("Not implemented")
