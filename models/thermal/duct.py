from core.model import Model
from core.variable import Variable


class Duct(Model):
    def __init__(self, name):
        self.name = name

        self.inputs = [
            Variable("Inlet flow"),
            Variable("Inlet temperature")
        ]

        self.outputs = [
            Variable("Outlet flow"),
            Variable("Outlet temperature")
        ]

    def run(self):
        self.get_output("Outlet flow").value = self.get_input("Inlet flow").value
        self.get_output("Outlet temperature").value = self.get_input("Inlet temperature").value / 2
