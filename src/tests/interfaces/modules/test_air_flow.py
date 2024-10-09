"""
Tests for the `air_flow.py` interface.
"""

import pandas as pd

from colibri.interfaces import AirFlow, Module


def test_air_flow() -> None:
    """Test the AirFLow class."""
    air_flow: AirFlow = AirFlow(
        name="air-flow-1",
        space_temperatures=dict(),
        sky_temperatures=pd.Series(dtype=float),
        exterior_air_temperatures=pd.Series(dtype=float),
        pressures=dict(),
        flow_rates=dict(),
    )
    assert isinstance(air_flow, AirFlow) is True
    assert isinstance(air_flow, Module) is True
    assert air_flow.name == "air-flow-1"


if __name__ == "__main__":
    test_air_flow()
