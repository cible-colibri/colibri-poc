"""
Plot class to help with plotting simulation variables.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from matplotlib.pyplot import Axes, Figure

from colibri.interfaces.module import Module

if TYPE_CHECKING:
    from colibri.core.fields import SimulationVariable


@dataclass
class Plot:
    """Class representing a plot."""

    name: str
    module: Module
    variable_name: str

    def add_plot_to_figure(
        self, figure: Figure, location: int, show_title: bool
    ) -> None:
        """Add the plot to the figure at the location.

        Returns
        -------
        figure : Figure
            Figure where the plot will be added
        location : int
            Location of the plot onto the figure
        show_title : bool = True
            Show title on each figure

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        axis: Axes = figure.add_subplot(location)
        if show_title is True:
            axis.set_title(self.name)
        series: List = getattr(self.module, f"{self.variable_name}_series")
        variable: SimulationVariable = self.module.get_field(self.variable_name)
        if not isinstance(series[0], dict):
            axis.plot(series, label=f"{self.module.name}.{variable.name}")
        if isinstance(series[0], dict):
            variables: dict = dict()
            for series_variable in series[-1]:
                variables[series_variable] = []
            for step in series:
                for k, v in step.items():
                    variables[k].append(v)
            for variable_name, values in variables.items():
                axis.plot(
                    values,
                    label=f"{self.module.name}.{variable.name}.{variable_name}",
                )
        axis.set_ylabel(f"[{variable.unit.value}]")
        axis.legend(loc="upper right", numpoints=1)
