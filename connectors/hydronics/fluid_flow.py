# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.variable_connector import VariableConnector

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class LiquidFlowConnector(VariableConnector):

    def __init__(self):
        self.connections = [
                                # (from_variable, to_variable)
                                ("inlet_temperature", "outlet_temperature"),
                                ("inlet_flow_rate", "outlet_flow_rate")
                            ]


# ========================================
# Functions
# ========================================
