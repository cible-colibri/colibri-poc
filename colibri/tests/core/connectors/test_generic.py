"""
This file tests the generic.py module in connectors/generics.
"""

import pytest

from colibri.core.connectors.generics.generic import GenericConnector
from colibri.core.variables.variable_connector import VariableConnector


@pytest.mark.short_test
def test_generic() -> None:
    """Test the behavior of GenericConnector."""
    connector: GenericConnector = GenericConnector()
    connector.add("from", "to")
    assert isinstance(connector, GenericConnector)
    assert isinstance(connector, VariableConnector)
    assert hasattr(connector, "add")
    assert isinstance(connector.connections, list)
    assert connector.connections[0] == ("from", "to")
    assert connector.__str__() == 'GenericConnector().add("from", "to")'
    assert connector.__repr__() == connector.__str__()


if __name__ == "__main__":
    test_generic()
