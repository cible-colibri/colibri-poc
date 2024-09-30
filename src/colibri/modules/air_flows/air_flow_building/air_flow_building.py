"""
AirFlowBuilding class from ThermalSpace interface.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Dict, Optional

import numpy as np

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import AirFlow
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


@unique
class Solvers(Enum):
    FULLY_ITERATIVE = "fully-iterative"
    PING_PONG = "ping-pong"


class AirFlowBuilding(AirFlow):
    def __init__(
        self,
        name: str,
        has_pressure_model: bool = False,
        internal_solver: Solvers = Solvers.FULLY_ITERATIVE,
    ):
        """Initialize a new ThermalSpaceSimplified instance."""
        super().__init__(
            name=name,
        )
        self.has_pressure_model = self.define_parameter(
            name="has_pressure_model",
            default_value=has_pressure_model,
            description="Specify whether or not a pressure model is used.",
            format=bool,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.internal_solver = self.define_parameter(
            name="internal_solver",
            default_value=internal_solver,
            description="Internal solver.",
            format=Solvers,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self._has_module_converged = False
        self.number_of_steps = 0

    def initialize(self) -> None:
        if self.has_pressure_model is True:
            self._has_module_converged = False
            self.internal_solver = "fully_iterative"

    def post_initialize(self) -> None:
        self.number_of_steps = len(self.sky_temperatures)

    def run(self, time_step: int, number_of_iterations: int) -> None:
        if self.has_pressure_model is False:
            return None
        # Maximum number of internal (th-p) iterations
        internal_maximum_number_of_iterations: int = 0
        # Reset parameters for next time step
        if number_of_iterations == 1:
            self._number_of_iterations = 0
            self._has_module_converged = False
            self.found = []
        # Pressure model
        if self.internal_solver is Solvers.FULLY_ITERATIVE:
            self.compute_pressures(
                time_step=time_step, number_of_iterations=number_of_iterations
            )
            self.check_pressures_convergence(
                number_of_iterations=number_of_iterations,
                internal_maximum_number_of_iterations=internal_maximum_number_of_iterations,
            )
        if self.internal_solver is Solvers.PING_PONG:
            while (
                not self._has_module_converged
                or self._number_of_iterations
                >= internal_maximum_number_of_iterations
            ) and (number_of_iterations == 0):
                self.compute_pressures(
                    time_step=time_step,
                    number_of_iterations=number_of_iterations,
                )
                self.check_pressures_convergence(
                    number_of_iterations=number_of_iterations,
                    internal_maximum_number_of_iterations=internal_maximum_number_of_iterations,
                )
                self._number_of_iterations += 1
        self.flow_rates = self.compute_flow_rates(
            spaces=self.project_data.spaces
        )
        self.found.append(np.sum(self.pressures))  # For convergence plotting
        # Save pressures for next time step as initial guess
        self.previous_pressures = self.pressures

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...
