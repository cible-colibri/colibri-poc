"""
This file tests the plot.py module in dataclasses.
"""

import pytest

from colibri.core.dataclasses.plot import Plot
from colibri.models.hydronics.duct import Duct


@pytest.mark.short_test
def test_plot():
    """Test the behavior of Plot."""
    duct_1: Duct = Duct("duct_1")
    plot: Plot = Plot("plot_1", duct_1, "outlet_temparature")
    assert isinstance(plot, Plot)
    assert hasattr(plot, "name")
    assert hasattr(plot, "model")
    assert hasattr(plot, "variable_name")
    assert (
        plot.__str__()
        == "Plot(name='plot_1', model=Duct(name = 'duct_1'), variable_name='outlet_temparature')"
    )
    assert plot.__repr__() == plot.__str__()


if __name__ == "__main__":
    test_plot()
