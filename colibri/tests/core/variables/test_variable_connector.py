"""
This file tests the variable_connector.py module in variables/.
"""

import pytest

from colibri.core.variables.variable_connector import VariableConnector


@pytest.mark.short_test
def test_variable_connector():
    """Test the behavior of VariableConnector."""
    connector = VariableConnector()
    connector.add("from", "to")
    assert isinstance(connector, VariableConnector)
    assert hasattr(connector, "connections")
    assert hasattr(connector, "add")
    assert isinstance(connector.connections, list)
    assert connector.connections[0] == ("from", "to")
    assert connector.__str__() == 'VariableConnector().add("from", "to")'
    assert connector.__repr__() == connector.__str__()


if __name__ == "__main__":
    test_variable_connector()
