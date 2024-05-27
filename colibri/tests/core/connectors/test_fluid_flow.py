"""
This file tests the fluid_flow.py module in connectors/generics.
"""

import pytest

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
from colibri.core.connectors.connector import Connector


@pytest.mark.short_test
def test_fluid_flow():
    """Test the behavior of FluidFlowConnector."""
    fluid_connector = FluidFlowConnector()
    assert isinstance(fluid_connector, FluidFlowConnector)
    assert isinstance(fluid_connector, Connector)
    assert hasattr(fluid_connector, "connections")
    assert hasattr(fluid_connector, "add")
    assert isinstance(fluid_connector.connections, list)
    assert fluid_connector.connections[0] == ("outlet_temperature", "inlet_temperature")
    assert fluid_connector.connections[1] == ("outlet_flow_rate", "inlet_flow_rate")
    assert fluid_connector.connections[-1] == ("outlet_flow_rate", "inlet_flow_rate")
    with pytest.raises(NotImplementedError):
        fluid_connector.add("from", "to")
    assert (
        fluid_connector.__str__()
        == 'FluidFlowConnector().add("outlet_temperature", "inlet_temperature").add("outlet_flow_rate", "inlet_flow_rate")'
    )
    assert fluid_connector.__repr__() == fluid_connector.__str__()


if __name__ == "__main__":
    test_fluid_flow()
