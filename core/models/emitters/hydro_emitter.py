import numpy as np

from core.templates.inputs import Inputs
from core.templates.outputs import Outputs
from core.templates.parameters import Parameters
from core.variables.variable import Variable
from core.models.emitters.emitter import Emitter
from utils.enums_utils import Roles, Units
from config.constants import CP_WATER

#TODO: faire une classe générique Emitter pour faciliter les associations automatiques
# Bien voir comment faire les liens entre objets/model pour faciliter la gestions des données au niveau initialisation

class HydroEmitter(Emitter):
    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        super(HydroEmitter, self).__init__(name, inputs, outputs, parameters)

        # parameters
        self.nominal_UA = Variable("nominal_UA", 0, role=Roles.PARAMETERS, unit=Units.WATT_PER_KELVIN, description="Nominal exchange coefficient at design conditions")
        self.nominal_flow_rate = Variable("nominal_flow_rate", 0, role=Roles.PARAMETERS, unit=Units.KILOGRAM_PER_SECOND, description="Nominal flow rate")
        self.deltaT_fluid_nom = Variable("deltaT_fluid_nom", 0, role=Roles.PARAMETERS, unit=Units.KELVIN, description="Nominal temperature difference between supply and return")
        self.nominal_heating_supply_temperature = Variable("nominal_heating_supply_temperature", 0, role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Nominal supply temperature for heating")
        self.nominal_cooling_supply_temperature = Variable("nominal_cooling_supply_temperature", 0, role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description="Nominal supply temperature for cooling")

        # input
        self.temperature_in = Variable("temperature_in", 0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS, description="Temperature going in the emitter")
        self.flow_rate = Variable("flow_rate", 0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_SECOND, description="Flow rate going through the emitter")

        # outputs
        self.temperature_out = Variable("temperature_out", 0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, description="Temperature going out of the emitter")

    def initialize(self) -> None:
        #TODO: for now imposed in the Thmodel...........
        #TODO: sizing automatique ? ou forcément par l'utilisateur ? si sizing automatique, voir comment on passe les infos -> centralisation au niveau du ThModel ?
        # idem, dictionnaire de valeurs par défaut ? ou directement dans la définition des variables au dessus ?
        self.deltaT_fluid_nom      = 10.
        self.nominal_heating_supply_temperature = 50.
        self.nominal_cooling_supply_temperature = 5.
        self.nominal_heating_power = 10000.  # same as in thmodel
        self.nominal_cooling_power = 0.  # same as in thmodel
        self.nominal_flow_rate     = self.nominal_heating_power / self.deltaT_fluid_nom / CP_WATER
        default_heating_set_point = 20.
        self.nominal_UA = np.abs(self.nominal_heating_power / (self.nominal_heating_supply_temperature - default_heating_set_point))

        #TODO: initialize results ?
        self.flow_rate = self.nominal_flow_rate
        self.temperature_in = self.nominal_heating_supply_temperature
        self.phi_radiative = 0.
        self.phi_convective = 0.
        self.phi_latent = 0.

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:

        self.phi_radiative  = self.heat_demand.value * self.radiative_share
        self.phi_convective = self.heat_demand.value * (1 - self.radiative_share)
        self.temperature_out = self.temperature_in - self.heat_demand / CP_WATER / self.flow_rate

    def iteration_done(self, time_step: int = 0):
        #TODO: ça j'ai pas compris si faut mettre tous les résultats ? Uniquement sur ceux où ça doit converger ?
        self.phi_radiative_last = self.phi_radiative

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")

    def check_units(self) -> None:
        pass

    def calc_convergence(self, threshold=1e-3):
        self.has_converged = np.sum(np.abs(self.phi_radiative - self.phi_radiative_last)) <= threshold
