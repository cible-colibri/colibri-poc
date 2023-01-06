class VariableConnector:

    def __init__(self):
        self.connections = []

    def add(self, from_variable_name, to_variable_name):
        self.connections.append((from_variable_name, to_variable_name))
