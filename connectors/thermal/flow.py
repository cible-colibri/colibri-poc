from core.variable_connector import VariableConnector


class LiquidFlowConnector(VariableConnector):
    def __init__(self):
        self.connections = [
            # (from_variable, to_variable)
            ("Inlet temperature", "Outlet temperature"),
            ("Inlet flowrate", "Outlet flowrate")
        ]
