class Model:
    def __init__(self, name: str):
        self.name = name
        self.inputs = []
        self.outputs = []

    @staticmethod
    def get_variable(name: str, variables: list) -> object:
        v = [i for i in variables if i.name == name]
        if len(v) > 0:
            return v[0]
        else:
            return None

    def get_output(self, name: str):
        return self.get_variable(name, self.outputs)

    def get_input(self, name: str):
        return self.get_variable(name, self.inputs)