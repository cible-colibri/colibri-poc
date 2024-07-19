import abc


from colibri.core.model import Model



from colibri.utils.enums_utils import Roles, Units


class Emitter(Model):
    def __init__(self, name: str):

        self.name = name
        self.project = None

        self.zone_name = self.field("zone_name", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="zone_name")
        self.radiative_share = self.field("radiative_share", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="radiative_share")
        self.nominal_heating_power = self.field("nominal_heating_power", 10000., role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal heating power")
        self.nominal_cooling_power = self.field("nominal_cooling_power", 10000., role=Roles.PARAMETERS, unit=Units.WATT, description="emitter absolute nominal cooling power")
        self.time_constant = self.field("time_constant", 0, role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter time constant")
        self.mode = self.field("mode", "reversible", role=Roles.PARAMETERS, unit=Units.UNITLESS, description="emitter emission mode (heating, cooling, reversible)")
        self.efficiency = self.field("efficiency", 0.9, role=Roles.PARAMETERS, unit=Units.UNITLESS,
                               description="emitter efficiency")

        # inputs
        self.heat_demand = self.field("heat_demand", 0, role=Roles.INPUTS, unit=Units.UNITLESS, description="heat_demand - positive=heating, negative=cooling")

        # outputs
        self.phi_radiative = self.field("phi_radiative", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Radiative part of thermal output")
        self.phi_convective = self.field("phi_convective", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Convective part of thermal output")
        self.phi_latent = self.field("phi_latent", 0, role=Roles.OUTPUTS, unit=Units.WATT, description="Latent part of thermal output")

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
    def calc_convergence(self, threshold=1e-3):
        raise NotImplementedError("Not implemented")
