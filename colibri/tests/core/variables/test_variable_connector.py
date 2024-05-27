"""
This file tests the connector.py module.
"""

import pytest

from colibri.core.connectors.connector import Connector


@pytest.mark.short_test
def test_variable_connector():
    """Test the behavior of Connector."""
    variable_connector = Connector()
    variable_connector.add("from", "to")
    assert isinstance(variable_connector, Connector)
    assert hasattr(variable_connector, "connections")
    assert hasattr(variable_connector, "add")
    assert isinstance(variable_connector.connections, list)
    assert variable_connector.connections[0] == ("from", "to")
    assert variable_connector.__str__() == 'Connector().add("from", "to")'
    assert variable_connector.__repr__() == variable_connector.__str__()


if __name__ == "__main__":
    test_variable_connector()
