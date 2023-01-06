from core.model import Model
from core.variable import Variable


class Duct(Model):
    def __init__(self, name):
        self.name = name
        self.inputs = [
            Variable("flow"),
            Variable("temperature")
        ]

        self.outputs = [
            Variable("flow"),
            Variable("temperature")
        ]

    def run(self):
        self.get_output("flow").value = self.get_input("flow").value
        self.get_output("temperature").value = self.get_input("temperature").value / 2
