"""
Tests for the `plot_utils.py` module.
"""

from matplotlib import pyplot as plt
from matplotlib.pyplot import Figure

from colibri.modules import AcvExploitationOnly
from colibri.utils.plot_utils import Plot


def test_plot() -> None:
    """Test the Plot class."""
    acv: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    setattr(acv, "co2_impact_series", [0, 1, 2, 3, 4])
    plot: Plot = Plot(name="plot-acv", module=acv, variable_name="co2_impact")
    assert plot.name == "plot-acv"
    assert plot.module is acv
    assert plot.variable_name == "co2_impact"
    assert hasattr(plot, "add_plot_to_figure")
    figure: Figure = plt.figure(figsize=(10, 8))
    assert figure.axes == []
    plot.add_plot_to_figure(figure=figure, location=222, show_title=True)
    assert len(figure.axes) == 1
    assert figure.axes[0].get_title() == "plot-acv"
    setattr(
        acv,
        "co2_impact_series",
        [{"fake-0": 0, "fake-1": 1}, {"fake-0": 0, "fake-1": 2}],
    )
    plot: Plot = Plot(name="plot-acv-2", module=acv, variable_name="co2_impact")
    figure: Figure = plt.figure(figsize=(10, 8))
    assert figure.axes == []
    plot.add_plot_to_figure(figure=figure, location=222, show_title=True)
    assert len(figure.axes) == 1
    assert figure.axes[0].get_title() == "plot-acv-2"
