# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from colibri.core.connectors.connector import Connector

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class FluidFlowConnector(Connector):

    def __init__(self):
        self.connections = [
                                # (from_variable, to_variable)
                                ("outlet_temperature", "inlet_temperature"),
                                ("outlet_flow_rate", "inlet_flow_rate")
                            ]


# ========================================
# Functions
# ========================================
