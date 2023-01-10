from core.model import Model
from core.variable import Variable
from core.variable_list import VariableList


class StorageTank(Model):
    def __init__(self, name):
        self.name = name

        self.inputs = []
        self.outputs = []

        self.inputs.append(Variable("Number of thermostats", 2))
        self.inputs.extend(
            VariableList(self, "Number of thermostats",
                [Variable("Height fraction of thermostat")]).expand())
        self.inputs.append(Variable("Inlet temperature for port-1"))
        self.inputs.append(Variable("Inlet temperature for port-2"))


        self.outputs = [
            Variable("Temperature at outlet 1"),
            Variable("Flow rate at outlet 1"),
            Variable("Temperature at outlet 2"),
            Variable("Flow rate at outlet 2")
        ]

    def run(self):
        self.get_output("Outlet flow").value = self.get_input("Inlet flow").value
        self.get_output("Outlet temperature").value = self.get_input("Inlet temperature").value / 2
