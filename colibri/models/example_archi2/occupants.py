import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles, Units)


class Occupants(Model):

    def __init__(self, name: str):
        self.name = name
        self.Tcons = self.field("Tcons", np.array(()), role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.QoccGains = self.field("QoccGains", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT)
        self.spaceSurface = self.field("spaceSurface", np.array(()), role=Roles.PARAMETERS, unit=Units.SQUARE_METER)
        self.TconsPresence = self.field("TconsPresence", np.array(()), role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)
        self.TconsAbsence = self.field("TconsAbsence", np.array(()), role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)
        self.scenarioPresence = self.field("scenarioPresence ", np.array(()), role=Roles.PARAMETERS, unit=Units.UNITLESS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        nbOccPerSquareMeter = 1/40
        singleOccupantPower = 100
        self.QoccGains = np.multiply(self.scenarioPresence, np.multiply(nbOccPerSquareMeter, np.multiply(self.spaceSurface, singleOccupantPower)))
        tcons = []
        for index, scenario in enumerate(self.scenarioPresence):
            if scenario[time_step] > 0:
                tcons.append(self.TconsPresence[index])
            else:
                tcons.append(self.TconsAbsence[index])
        self.Tcons = np.array(tcons)

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass
