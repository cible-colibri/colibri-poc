from core.variable_connector import VariableConnector


class LiquidFlowConnector(VariableConnector):
    def __init__(self):
        self.connections = [
            ("Inlet temperature", "Outlet temperature"),
            ("Inlet flowrate", "Outlet flowrate")
        ]
