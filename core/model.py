from core.variable_list import VariableList


class Model:
    def __init__(self, name: str):
        self.name = name
        self.inputs = []
        self.outputs = []

    @staticmethod
    def get_variable(name: str, variables: list) -> object:
        for v in variables:
            if v.name == name:
                return v


    def get_output(self, name: str):
        return self.get_variable(name, self.outputs)

    def get_input(self, name: str):
        return self.get_variable(name, self.inputs)

    def set(self, variable_name: str, value: float):
        # set value and expand vectors
        pass

    def get(self, variable_name: str):
        # set value and expand vectors
        v = [v for v in self.inputs + self.outputs if v.name == variable_name]
        if len(v) == 1:
            return v[0]
        else:
            return None

    def run(self):
        pass

    def init(self):
        pass

    def iteration_done(self):
        pass

    def simulation_done(self):
        pass