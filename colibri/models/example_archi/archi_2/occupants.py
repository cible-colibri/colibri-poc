import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles, Units)


class Occupants(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.Tcons = Variable("Tcons", np.array(()), role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.QoccGains = Variable("QoccGains", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT)
        self.spaceSurface = Variable("spaceSurface", np.array(()), role=Roles.PARAMETERS, unit=Units.SQUARE_METER)
        self.TconsPresence = Variable("TconsPresence", np.array(()), role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)
        self.TconsAbsence = Variable("TconsAbsence", np.array(()), role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)
        self.scenarioPresence = Variable("scenarioPresence ", np.array(()), role=Roles.PARAMETERS, unit=Units.UNITLESS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        nbOccPerSquareMeter = 1/40
        singleOccupantPower = 100
        self.QoccGains = np.multiply(self.scenarioPresence, np.multiply(nbOccPerSquareMeter, np.multiply(self.spaceSurface, singleOccupantPower)))
        tcons = []
        for index, scenario in enumerate(self.scenarioPresence.value):
            if scenario[time_step] > 0:
                tcons.append(self.TconsPresence.value[index])
            else:
                tcons.append(self.TconsAbsence.value[index])
        self.Tcons = np.array(tcons)

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass