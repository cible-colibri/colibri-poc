import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import Roles


class Aggregation(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.element = self.field("element", 0.0, role=Roles.INPUTS)
        self.elements = self.field("elements", np.array(()), role=Roles.OUTPUTS)
        self.multiplicator = self.field("multiplicator", 1, role=Roles.PARAMETERS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.elements = np.array([self.element] * self.multiplicator)

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass


class Multiplication(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.element = self.field("element", 0.0, role=Roles.INPUTS)
        self.elements = self.field("elements", np.array(()), role=Roles.OUTPUTS)
        self.multiplicator = self.field("multiplicator", 1, role=Roles.PARAMETERS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.elements = np.array([self.element] * self.multiplicator)

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass


class Stack(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.elements = self.field("elements", np.array(()), role=Roles.OUTPUTS)
        self._stack = []

    def add(self, model: Model, variable: str):
        self._stack.append((model, variable))
        return self

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.elements = np.array([model for model in self._stack])

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass


class Summation(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.elements = self.field("elements", np.array(()), role=Roles.INPUTS)
        self.sum = self.field("sum", 0.0, role=Roles.OUTPUTS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        # BUG: Error when summing without value
        self.sum = np.sum(self.elements)

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass