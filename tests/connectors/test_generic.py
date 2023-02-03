# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from connectors.generics.generic import GenericConnector
from core.variable_connector     import VariableConnector

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

def test_generic():
    connector = GenericConnector()
    connector.add("from", "to")
    assert isinstance(connector, GenericConnector)
    assert isinstance(connector, VariableConnector)
    assert hasattr(connector, "add")
    assert isinstance(connector.connections, list)
    assert connector.connections[0] == ("from", "to")
    assert connector.__str__() == "GenericConnector().add([('from', 'to')])"
    assert connector.__repr__() == connector.__str__()


if __name__ == "__main__":
    test_generic()
