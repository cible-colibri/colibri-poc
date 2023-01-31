import numpy as np

from core.model import Model
from core.variable import Variable
from core.variable_list import VariableList


class StorageTank(Model):
    def __init__(self, name):
        self.name = name

        self.inputs = []
        self.outputs = []

        self.inputs.append(Variable("Number_of_tank_nodes", 2))
        self.inputs.extend(
            VariableList(self, "Number_of_tank_nodes",
                [Variable("Height_node")]).expand())

        self.inputs.append(Variable("Initial_temperature"))

        self.inputs.append(Variable("inlet_temperature_1", 40))
        self.inputs.append(Variable("inlet_flow_rate_1", 100))
        self.inputs.append(Variable("inlet_temperature_2", 40))
        self.inputs.append(Variable("inlet_flow_rate_2", 100))


        self.outputs = [
            Variable("outlet_temperature_1"),
            Variable("outlet_flow_rate_1"),
            Variable("outlet_temperature_2"),
            Variable("outlet_flow_rate_2"),
        ]

        self.node_temperatures = None

    def initialize(self):
        self.node_temperatures = np.ones(self.Number_of_tank_nodes.value) * self.Initial_temperature

    def run(self, time_step):
        self.outlet_flow_rate_1 = self.inlet_flow_rate_1
        self.outlet_flow_rate_2 = self.inlet_flow_rate_2
        self.outlet_temperature_1 = self.inlet_temperature_1
        self.outlet_temperature_2 = self.inlet_temperature_2

        self.node_temperatures[:] =  self.get_input("inlet_temperature_1").value
        self.node_temperatures[:-1] = self.get_output("outlet_temperature_1").value

        pass
