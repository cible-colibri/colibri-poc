from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.field import Field
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class LayerWallLosses(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        super(LayerWallLosses, self).__init__(name)

        self.Text = self.field("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Boundaries = self.field("Boundaries", [], role=Roles.INPUTS, unit=Units.OBJECT_LIST,
                                   structure = [
                                       Field('thermal_conductivity', 0, Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('thickness', 0, Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('area', 0, Roles.PARAMETERS, Units.SQUARE_METER),
                                       Field('space.Tint', 0, Roles.INPUTS, Units.DEGREE_CELSIUS)
                                   ])

        self.Qwall = self.field("Qwall", {}, role=Roles.OUTPUTS, unit=Units.DICTIONARY)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for boundary in self.Boundaries:
            space = boundary.space
            if space:
                Tint = space.Tint # get value from store ('backbone')
                e = boundary.thickness
                Lambda = boundary.thermal_conductivity

                boundary.R = sum(e1 / Lambda1 for e1, Lambda1 in zip(e, Lambda))
                boundary.U = 1 / boundary.R

                Qwall[boundary.label] = boundary.U * boundary.area * (Tint - self.Text)
                setattr(boundary, 'Qwall', Qwall[boundary.label]) # upload value to store

        self.Qwall = Qwall


    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.get_fields(Roles.OUTPUTS):
            print(f"{output.name}={getattr(self, output.name)}")
