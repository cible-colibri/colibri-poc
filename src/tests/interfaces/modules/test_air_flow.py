"""
Tests for the `air_flow.py` interface.
"""

import pytest

from colibri.interfaces import AirFlow, Module


@pytest.mark.xfail(reason="in progress...")
def test_air_flow() -> None:
    """Test the AirFLow class."""
    air_flow: AirFlow = AirFlow(
        name="air-flow-1",
        pressures=dict(),
        flow_rates=dict(),
    )
    assert isinstance(air_flow, AirFlow) is True
    assert isinstance(air_flow, Module) is True
    assert air_flow.name == "air-flow-1"


if __name__ == "__main__":
    test_air_flow()
