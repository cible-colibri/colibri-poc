"""
This file tests the generic.py module in connectors/generics.
"""

import pytest

from colibri.core.connectors.generics.generic import GenericConnector
from colibri.core.connectors.connector import Connector


@pytest.mark.short_test
def test_generic() -> None:
    """Test the behavior of GenericConnector."""
    generic_connector: GenericConnector = GenericConnector()
    generic_connector.add("from", "to")
    assert isinstance(generic_connector, GenericConnector)
    assert isinstance(generic_connector, Connector)
    assert hasattr(generic_connector, "add")
    assert isinstance(generic_connector.connections, list)
    assert generic_connector.connections[0] == ("from", "to")
    assert generic_connector.__str__() == 'GenericConnector().add("from", "to")'
    assert generic_connector.__repr__() == generic_connector.__str__()


if __name__ == "__main__":
    test_generic()
