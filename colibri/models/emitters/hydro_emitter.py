import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.templates.outputs import Outputs
from colibri.core.templates.parameters import Parameters
from colibri.core.variables.variable import Variable
from colibri.models.emitters.emitter import Emitter
from colibri.utils.enums_utils import Roles, Units
from colibri.core.constants import CP_WATER

#TODO: faire une classe générique Emitter pour faciliter les associations automatiques
# Bien voir comment faire les liens entre objets/model pour faciliter la gestions des données au niveau initialisation

class HydroEmitter(Emitter):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        super(HydroEmitter, self).__init__(name, inputs, outputs, parameters)

        # parameters
        self.nominal_UA = self.field("nominal_UA", 330., role=Roles.PARAMETERS, unit=Units.WATT_PER_KELVIN, description="Nominal exchange coefficient at design conditions")
        self.nominal_flow_rate = self.field("nominal_flow_rate", 0.24, role=Roles.PARAMETERS, unit=Units.KILOGRAM_PER_SECOND, description="Nominal flow rate")
        self.deltaT_fluid_nom = self.field("deltaT_fluid_nom", 10., role=Roles.PARAMETERS, unit=Units.KELVIN, description="Nominal temperature difference between supply and return")
        self.nominal_heating_supply_temperature = self.field("nominal_heating_supply_temperature", 50., role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Nominal supply temperature for heating")
        self.nominal_cooling_supply_temperature = self.field("nominal_cooling_supply_temperature", 5., role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Nominal supply temperature for cooling")
        self.default_heating_set_point = self.field("default_set_point", 20., role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Default set point use for the nominal_UA calculation (P / (Tsupply - Tsetpoint))")
        self.default_cooling_set_point = self.field("default_set_point", 27., role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Default set point use for the nominal_UA calculation (P / (Tsupply - Tsetpoint))")

        # input
        self.temperature_in = self.field("temperature_in", 0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS, description="Temperature going in the emitter")
        self.flow_rate = self.field("flow_rate", 0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_SECOND, description="Flow rate going through the emitter")

        # outputs
        self.temperature_out = self.field("temperature_out", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="Temperature going out of the emitter")

    def initialize(self) -> None:

        #TODO: sizing automatique ? ou forcément par l'utilisateur ? si sizing automatique, voir comment on passe les infos -> centralisation au niveau du ThModel ?
        if self.mode == 'cooling':
            self.nominal_heating_power = 0.
            self.temperature_in = self.nominal_cooling_supply_temperature
            self.temperature_out = self.nominal_cooling_supply_temperature + self.deltaT_fluid_nom
        elif self.mode == 'heating':
            self.nominal_cooling_power = 0.
            self.temperature_in = self.nominal_heating_supply_temperature
            self.temperature_out = self.nominal_heating_supply_temperature - self.deltaT_fluid_nom
        else:
            self.temperature_in = self.nominal_heating_supply_temperature
            self.temperature_out = self.nominal_heating_supply_temperature - self.deltaT_fluid_nom

        self.nominal_flowrate = max(self.nominal_heating_power, self.nominal_heating_power) / CP_WATER / self.deltaT_fluid_nom

        nominal_UA_heating = np.abs(self.nominal_heating_power / (self.nominal_heating_supply_temperature - self.default_heating_set_point))
        nominal_UA_cooling = np.abs(self.nominal_cooling_power / (self.default_cooling_set_point - self.nominal_cooling_supply_temperature))
        self.nominal_UA = max(nominal_UA_heating, nominal_UA_cooling)

        # initialize inputs/outputs
        self.flow_rate = self.nominal_flow_rate
        self.temperature_in = self.nominal_heating_supply_temperature
        self.phi_radiative = 0.
        self.phi_convective = 0.
        self.phi_latent = 0.

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.phi_radiative   = self.heat_demand * self.radiative_share
        self.phi_convective  = self.heat_demand * (1 - self.radiative_share)
        self.temperature_out = self.temperature_in - self.heat_demand / CP_WATER / self.flow_rate

    def iteration_done(self, time_step: int = 0):
        self.temperature_out_last = self.temperature_out

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")

    def check_units(self) -> None:
        pass

    def calc_convergence(self, threshold=1e-3):
        self.has_converged = np.sum(np.abs(self.temperature_out - self.temperature_out_last)) <= threshold
