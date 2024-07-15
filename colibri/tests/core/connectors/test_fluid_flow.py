# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
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


# ========================================
# Functions
# ========================================

@pytest.mark.short_test
def test_fluid_flow():
    fluid_connector = FluidFlowConnector()
    fluid_connector.add("from", "to")
    assert isinstance(fluid_connector, FluidFlowConnector)
    assert isinstance(fluid_connector, Connector)
    assert hasattr(fluid_connector, "add")
    assert isinstance(fluid_connector.connections, list)
    assert fluid_connector.connections[0] == ("outlet_temperature", "inlet_temperature")
    assert fluid_connector.connections[1] == ("outlet_flow_rate", "inlet_flow_rate")
    assert fluid_connector.connections[-1] == ("from", "to")
    assert fluid_connector.__str__() == "FluidFlowConnector().add(('outlet_temperature', 'inlet_temperature')).add(('outlet_flow_rate', 'inlet_flow_rate')).add(('from', 'to'))"
    assert fluid_connector.__repr__() == fluid_connector.__str__()


if __name__ == "__main__":
    test_fluid_flow()
