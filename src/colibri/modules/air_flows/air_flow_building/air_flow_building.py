"""
AirFlowBuilding class from ThermalSpace interface.
"""

from __future__ import annotations

import traceback
from enum import Enum, unique
from typing import Any, Dict, List, Optional

import numpy as np
from numpy import ndarray
from pandas import Series

from colibri.config.constants import UNIT_CONVERTER
from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import AirFlow
from colibri.modules.air_flows.air_flow_building.boundary_conditions import (
    compute_boundary_conditions,
)
from colibri.modules.air_flows.air_flow_building.connection_functions import (
    compute_pressure_loss_for_mechanical_fans,
)
from colibri.modules.air_flows.air_flow_building.utilities import (
    construct_boundary_and_space_nodes,
    construct_flow_resistance_coefficient_matrices,
    generate_relaxation_space_flow_resistance_nodes,
    generate_system_and_control_pressure_matrices,
    get_fan_suction_nodes,
)
from colibri.modules.modules_constants import (
    ATMOSPHERIC_AIR_PRESSURE,
    DENSITY_AIR,
    GRAVITATIONAL_ACCELERATION,
    REFERENCE_AIR_TEMPERATURE,
    RS_AIR,
)
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)
from colibri.utils.exceptions_utils import UserInputError


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
        space_temperatures: Dict[str, ndarray] = None,
        sky_temperatures: Series = None,
        exterior_air_temperatures: Series = None,
        pressures: Dict[str, ndarray] = None,
        flow_rates: List[List[Any]] = None,
        flow_paths: List[Dict[str, Any]] = None,
        project_data: Optional[ProjectData] = None,
    ):
        """Initialize a new ThermalSpaceSimplified instance."""
        if space_temperatures is None:
            space_temperatures: Dict[str, ndarray] = dict()
        if pressures is None:
            pressures: Dict[str, ndarray] = dict()
        if flow_rates is None:
            flow_rates: List[List[Any]] = []
        super().__init__(
            name=name,
            space_temperatures=space_temperatures,
            sky_temperatures=sky_temperatures,
            exterior_air_temperatures=exterior_air_temperatures,
            pressures=pressures,
            flow_rates=flow_rates,
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
        self.flow_paths = self.define_parameter(
            name="flow_paths",
            default_value=flow_paths,
            description="Flow paths.",
            format=List[Dict[str, Any]],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.project_data = self.define_parameter(
            name="project_data",
            default_value=project_data,
            description="Project data.",
            format=ProjectData,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=[
                Parameter(
                    name="pn",
                    default_value=None,
                    description="Nominal power.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=False,
                    ),
                ),
                Parameter(
                    name="efficiency",
                    default_value=0.8,
                    description="Efficiency of the emitter.",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=True,
                    ),
                ),
            ],
        )

        self._has_module_converged = False
        self.number_of_steps = 0

    def initialize(self) -> None:
        if self.has_pressure_model is True:
            self._has_module_converged = False
            self.internal_solver = "fully_iterative"

    def post_initialize(self) -> None:
        self.number_of_steps = len(self.sky_temperatures)
        compute_boundary_conditions(
            exterior_air_temperatures=self.exterior_air_temperatures,
            boundary_conditions=self.project_data.boundary_conditions,
            number_of_time_steps=self.number_of_steps,
            dynamic_test=1,
            apply_disturbance=[24, 0],
        )
        # Simulate with pressure model
        if self.has_pressure_model:
            try:
                self._initialize_matrix_model()
            except Exception as error:
                error_message: str = (
                    f"Pressure configuration does not"
                    f" correspond to thermal spaces. "
                    f"Change to pressure_model == False "
                    f"or correct.\n"
                    f"[{type(error).__name__}]"
                    f"{traceback.format_exc()}"
                )
                raise UserInputError(error_message)
            self._has_module_converged = False
            self.internal_solver = Solvers.FULLY_ITERATIVE
        # Simulate without pressure model
        if not self.has_pressure_model:
            self.flow_paths = self.nodes = self.flow_array = []
            self.pressures = 0
            self.previous_pressures = 0
            self._has_module_converged = True
        # For convergence plot of pressure model
        self.found = []

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
            self._compute_pressures(
                time_step=time_step, number_of_iterations=number_of_iterations
            )
            self._check_pressures_convergence(
                number_of_iterations=number_of_iterations,
                internal_maximum_number_of_iterations=internal_maximum_number_of_iterations,
            )
        if self.internal_solver is Solvers.PING_PONG:
            while (
                not self._has_module_converged
                or self._number_of_iterations
                >= internal_maximum_number_of_iterations
            ) and (number_of_iterations == 0):
                self._compute_pressures(
                    time_step=time_step,
                    number_of_iterations=number_of_iterations,
                )
                self._check_pressures_convergence(
                    number_of_iterations=number_of_iterations,
                    internal_maximum_number_of_iterations=internal_maximum_number_of_iterations,
                )
                self._number_of_iterations += 1
        # Store flow rate values for thermal model
        self._compute_flow_rates()
        # For convergence plotting
        self.found.append(np.sum(self.pressures))
        # Save pressures for next time step as initial guess
        self.previous_pressures = self.pressures

        print(
            f"[{time_step = } | {number_of_iterations = }] {self.flow_rates = } | {self.pressures = }"
        )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return self._has_module_converged

    def _initialize_matrix_model(self) -> None:
        # Define boundary and system pressure nodes
        (
            self.boundary_condition_indices,
            self.boundary_condition_names,
            self.boundary_condition_pressures,
            self.space_indices,
            self.space_names,
        ) = construct_boundary_and_space_nodes(
            spaces=self.project_data.spaces,
            boundary_conditions=self.project_data.boundary_conditions,
        )
        # Flow resistance coefficient (kb) matrices
        # CCa, CCb, n_CCa, n_CCb, BB_flow, U_flow_indexer, U_fan_index
        (
            self.space_flow_resistance_nodes,
            self.boundary_and_space_flow_resistance_nodes,
            self.exponent_space_flow_resistance_nodes,
            self.exponent_boundary_and_space_flow_resistance_nodes,
            self.imposed_flow_rates,
            self.flows,
            self.fans,
        ) = construct_flow_resistance_coefficient_matrices(
            flow_paths=self.flow_paths,
            boundary_condition_names=self.boundary_condition_names,
            space_names=self.space_names,
        )
        # Check that everything is connected as it should
        self.fan_suction_nodes = get_fan_suction_nodes(
            flow_paths=self.flow_paths,
            boundary_condition_names=self.boundary_condition_names,
        )

        # Connectivity tables ( to act like in sparse)
        # CTa
        self.connectivity_space_flow_resistance_nodes = np.argwhere(
            np.abs(self.space_flow_resistance_nodes) > 1e-30
        )
        # CTb
        self.connectivity_boundary_and_space_flow_resistance_nodes = (
            np.argwhere(
                np.abs(self.boundary_and_space_flow_resistance_nodes) > 1e-30
            )
        )

        # Initialize flow matrices
        number_of_spaces: int = len(self.space_indices)
        number_of_boundary_conditions: int = len(
            self.boundary_condition_indices
        )
        # Any value, just for initializing
        nominal_flow_rate = 10.0 / 3600.0 * DENSITY_AIR
        # Initial flow matrices with nominal flow rate in all segments
        # FFa
        self.space_flow_matrices = (
            np.ones((number_of_spaces, number_of_spaces)) * nominal_flow_rate
        )
        # FFb
        self.boundary_condition_flow_matrices = (
            np.ones((number_of_spaces, number_of_boundary_conditions))
            * nominal_flow_rate
        )
        # Initial flow matrices for relaxation with nominal flow rate in all segments
        # FFa_act
        self.relaxation_space_flow_matrices = (
            np.ones((number_of_spaces, number_of_spaces)) * nominal_flow_rate
        )
        # FFb_act
        self.relaxation_boundary_condition_flow_matrices = (
            np.ones((number_of_spaces, number_of_boundary_conditions))
            * nominal_flow_rate
        )

        # Initial states of Network
        # Initial node pressures to 0
        self.pressures = np.zeros((number_of_spaces, 1))
        # Set a different pressure for previous time step
        self.previous_pressures = np.zeros((number_of_spaces, 1)) + 20.0
        # Initialize results
        self.pressure_results = np.zeros(
            (self.number_of_steps, number_of_spaces)
        )
        # Boundary condition connection arrays (U_pressure)
        # N pressure nodes in boundary
        self.boundary_pressures = np.zeros((number_of_boundary_conditions, 1))
        # N injection nodes for flow rate by fans (U_flow)
        self.boundary_flows = np.zeros((number_of_boundary_conditions, 1))

    def _compute_pressures(
        self, time_step: int, number_of_iterations: int
    ) -> None:
        # Pressure for boundary conditions
        for boundary_index, boundary_condition in enumerate(
            self.project_data.boundary_conditions
        ):
            # Eventual correction (fan, etc.)
            pressure_difference_correction: float = 0.0
            boundary_condition.pressure = boundary_condition.pressures[
                time_step
            ]
            boundary_condition.exterior_air_temperature = (
                boundary_condition.exterior_air_temperatures[time_step]
            )
            boundary_density: float = ATMOSPHERIC_AIR_PRESSURE / (
                RS_AIR
                * UNIT_CONVERTER.convert(
                    value=boundary_condition.exterior_air_temperature,
                    unit_from=Units.DEGREE_CELSIUS,
                    unit_to=Units.KELVIN,
                )
            )
            exterior_density: float = ATMOSPHERIC_AIR_PRESSURE / (
                RS_AIR
                * UNIT_CONVERTER.convert(
                    value=-REFERENCE_AIR_TEMPERATURE,
                    unit_from=Units.DEGREE_CELSIUS,
                    unit_to=Units.KELVIN,
                )
            )
            # Pressure correction
            pressure_difference_correction -= (
                (exterior_density - boundary_density)
                * GRAVITATIONAL_ACCELERATION
                * boundary_condition.z_relative_position
            )
            if boundary_condition.id in self.fan_suction_nodes:
                for fan in self.fans:
                    # fan[2] -> right one (name of the boundary condition)
                    if boundary_condition.id == fan[2]:
                        id_from: int = fan[1]
                        id_to: int = fan[3]
                        connection: str = fan[0]["connection"]
                        flow_rate: float = (
                            self.relaxation_boundary_condition_flow_matrices[
                                id_to, id_from
                            ]
                        )
                        sign: int = fan[4]
                        pressure_difference_correction += (
                            sign
                            * compute_pressure_loss_for_mechanical_fans(
                                flow_rate=flow_rate * 3600 / DENSITY_AIR,
                                delta_pressure_law=connection["pressure_curve"],
                            )
                        )
            boundary_condition.pressure += pressure_difference_correction
            self.boundary_pressures[boundary_index, 0] = (
                boundary_condition.pressure
            )
        # Fan flow rates (imposed flow rates in pressure model)
        for flow in self.flows:
            connection: str = flow[0]["connection"]
            flow_rate: float = connection["flow_rate"] / 3600.0
            self.boundary_flows[flow[1], 0] = (
                flow_rate  # TODO: Check for sign!!!
            )
        # Use average flow with relaxation factor to update flow rate
        if number_of_iterations > 0:
            smoothie: float = 0.5
            self.relaxation_space_flow_matrices = (
                self.space_flow_matrices * smoothie
                + self.relaxation_space_flow_matrices * (1 - smoothie)
            )
            self.relaxation_boundary_condition_flow_matrices = (
                self.boundary_condition_flow_matrices * smoothie
                + self.relaxation_boundary_condition_flow_matrices
                * (1 - smoothie)
            )
        # Generate the CCa_act and CCb_act matrices. with : C_act = C * flow_last_it ** (1/n-1)
        (
            self.relaxation_space_flow_resistance_nodes,
            self.relaxation_boundary_and_space_flow_resistance_nodes,
        ) = generate_relaxation_space_flow_resistance_nodes(
            space_flow_resistance_nodes=self.space_flow_resistance_nodes,
            boundary_and_space_flow_resistance_nodes=self.boundary_and_space_flow_resistance_nodes,
            connectivity_space_flow_resistance_nodes=self.connectivity_space_flow_resistance_nodes,
            connectivity_boundary_and_space_flow_resistance_nodes=self.connectivity_boundary_and_space_flow_resistance_nodes,
            exponent_space_flow_resistance_nodes=self.exponent_space_flow_resistance_nodes,
            exponent_boundary_and_space_flow_resistance_nodes=self.exponent_boundary_and_space_flow_resistance_nodes,
            relaxation_space_flow_matrices=self.relaxation_space_flow_matrices,
            relaxation_boundary_condition_flow_matrices=self.relaxation_boundary_condition_flow_matrices,
        )
        # Set the space flow matrix (system pressure matrix, A) FFa,
        # boundary condition flow matrix (control pressure matrix, B) FFb
        # and pressure matrix (P)
        (
            self.pressures,
            self.space_flow_matrices,
            self.boundary_condition_flow_matrices,
        ) = generate_system_and_control_pressure_matrices(
            boundary_pressures=self.boundary_pressures,
            boundary_flows=self.boundary_flows,
            relaxation_space_flow_resistance_nodes=self.relaxation_space_flow_resistance_nodes,
            relaxation_boundary_and_space_flow_resistance_nodes=self.relaxation_boundary_and_space_flow_resistance_nodes,
            imposed_flow_rates=self.imposed_flow_rates,
            flow_paths=self.flow_paths,
            spaces=self.project_data.spaces,
            boundary_conditions=self.project_data.boundary_conditions,
            space_temperatures=self.space_temperatures,
        )

    def _check_pressures_convergence(
        self,
        number_of_iterations: int,
        internal_maximum_number_of_iterations: int,
    ) -> None:
        """Check pressure convergence between previous and current time steps
           Convergence if ΔP <= 1e-7 or maximum number of iterations reached

        Parameters
        ----------
        number_of_iterations : int
            Number of iterations
        internal_maximum_number_of_iterations : int
            Maximum number of iterations to reach convergence

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Check for difference from last time step
        # Relative change from last iteration compared
        # to reference pressure ATMOSPHERIC_AIR_PRESSURE
        pressure_differences: ndarray = (
            np.abs(self.pressures - self.previous_pressures)
            / ATMOSPHERIC_AIR_PRESSURE
        )
        # Take the maximum difference from all pressure nodes
        pressure_difference_max: float = np.abs(np.max(pressure_differences))
        # Check for convergence
        # Convergence if ΔP <= 1e-7 or maximum number of iterations reached
        if (pressure_difference_max <= 1e-7) or (
            number_of_iterations > internal_maximum_number_of_iterations
        ):
            self._has_module_converged = True
        else:
            self._has_module_converged = False
        # Keep pressure vector for next iteration step
        self.previous_pressures = self.pressures

    def _compute_flow_rates(self) -> None:
        """Compute flow rates

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        flow_rates: List[Dict[str, Any]] = []
        for flow_path in self.flow_paths:
            path: List[str] = flow_path["path"]
            sign: int = flow_path["flow_sign"]
            index_from: int = flow_path["path_ids"][0]
            index_to: int = flow_path["path_ids"][1]
            flow_rate: float = (
                sign
                * self.boundary_condition_flow_matrices[index_from, index_to]
                * 3600
                if flow_path["flow_matrix"] == "FFb"
                else sign
                * self.space_flow_matrices[index_from, index_to]
                * 3600
            )
            for space in self.project_data.spaces:
                if (path[0] == space.id) and (flow_rate < 0):
                    # from other space into current space
                    flow_rates.append([path[1], path[0], -flow_rate])
                if (path[1] == space.id) and (flow_rate > 0):
                    flow_rates.append([path[0], path[1], flow_rate])
        self.flow_rates = flow_rates


if __name__ == "__main__":
    import pandas as pd
    from pandas import DataFrame

    from colibri.core import ProjectData
    from colibri.project_objects import BoundaryCondition, Space

    space_1: Space = Space(
        id="living-room",
        label="living-room",
        volume=52.25,
        reference_area=20.9,
    )
    space_2: Space = Space(
        id="kitchen",
        label="kitchen",
        volume=23.8,
        reference_area=9.52,
    )
    spaces: List[Space] = [space_1, space_2]
    boundary_condition_1: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-1",
        label="living room exterior boundary condition",
        z_relative_position=0,
        pressure=0,
    )
    boundary_condition_2: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-2",
        label="kitchen exterior boundary condition",
        z_relative_position=0,
        pressure=0,
    )
    boundary_conditions: List[BoundaryCondition] = [
        boundary_condition_1,
        boundary_condition_2,
    ]
    project_data: ProjectData = ProjectData(name="project-data-1", data=None)
    project_data.spaces = spaces
    project_data.boundary_conditions = boundary_conditions
    flow_paths: List[Dict[str, Any]] = [
        {
            "path": ["boundary-condition-1", "living-room"],
            "z": 0,
            "connection": {
                "connection_type": "inlet_grille",
                "dp0": 20,
                "rho0": DENSITY_AIR,
                "flow0": 30,
                "n": 0.5,
            },
        },
        {
            "path": ["living-room", "kitchen"],
            "z": 0,
            "connection": {
                "connection_type": "door",
                "section": 0.008,
                "discharge_coefficient": 0.6,
                "n": 0.5,
            },
        },
        {
            "path": ["kitchen", "boundary-condition-2"],
            "z": 0,
            "connection": {
                "connection_type": "outlet_grille",
                "dp0": 80,
                "rho0": DENSITY_AIR,
                "flow0": 45,
                "n": 0.5,
            },
        },
    ]
    air_flow_building: AirFlowBuilding = AirFlowBuilding(
        name="air-flow-1",
        project_data=project_data,
        flow_paths=flow_paths,
        has_pressure_model=True,
    )
    data: DataFrame = pd.read_csv(
        r"D:\developments\versioned\colibri\colibri\src\colibri\sky_temperatures.csv",
        sep=",",
        names=["sky_temperatures", "exterior_air_temperatures"],
        header=1,
    )
    # data["exterior_air_temperatures"] = pd.to_numeric(data["exterior_air_temperatures"])
    # data["exterior_air_temperatures"] = data["exterior_air_temperatures"].astype(float)
    # data["exterior_air_temperatures"] = data["exterior_air_temperatures"].fillna(data["exterior_air_temperatures"].rolling(window=6, min_periods=1).mean())
    # data.to_csv(r"D:\developments\versioned\colibri\colibri\src\colibri\sky_temperatures_2.csv", index=False)
    air_flow_building.initialize()
    air_flow_building.sky_temperatures = data["sky_temperatures"].to_numpy()
    air_flow_building.exterior_air_temperatures = data[
        "exterior_air_temperatures"
    ].to_numpy()
    air_flow_building.post_initialize()

    """
    print(f"{air_flow_building.imposed_flow_rates = }")
    print(f"{air_flow_building.space_flow_resistance_nodes = }")
    print(f"{air_flow_building.boundary_and_space_flow_resistance_nodes = }")
    print(f"{air_flow_building.connectivity_space_flow_resistance_nodes = }")
    print(f"{air_flow_building.connectivity_boundary_and_space_flow_resistance_nodes = }")
    print(f"{air_flow_building.space_flow_matrices = }")
    print(f"{air_flow_building.relaxation_space_flow_matrices = }")
    print(f"{air_flow_building.boundary_condition_flow_matrices = }")
    print(f"{air_flow_building.relaxation_boundary_condition_flow_matrices = }")
    print(f"{air_flow_building.fans = }")
    print(f"{air_flow_building.flows = }")
    print(f"{air_flow_building.boundary_condition_indices = }")
    print(f"{air_flow_building.boundary_condition_names = }")
    print(f"{air_flow_building.boundary_condition_pressures = }")
    print(f"{air_flow_building.exponent_space_flow_resistance_nodes = }")
    print(f"{air_flow_building.exponent_boundary_and_space_flow_resistance_nodes = }")
    print(f"{air_flow_building.space_indices = }")
    print(f"{air_flow_building.space_names = }")
    """

    def _substitute_links_values(
        air_flow_building: AirFlowBuilding, space_temperatures, time_step
    ) -> None:
        air_flow_building.space_temperatures = {
            "kitchen": space_temperatures["kitchen_1"][time_step],
            "living-room": space_temperatures["living_room_1"][time_step],
        }
        # print(air_flow_building.space_temperatures)

    import json

    with open(
        r"D:\developments\versioned\colibri\colibri\src\colibri\temperatures.json",
        "r",
    ) as _f:
        space_temperatures = json.load(_f)

    n_max_iterations = 100
    non_convergence_times = []
    iterate = True
    n_iteration = 1
    for time_step in range(0, 48):
        number_of_iterations = 1
        _has_converged = False
        while not _has_converged:
            _has_converged = True
            _substitute_links_values(
                air_flow_building, space_temperatures, time_step
            )
            air_flow_building.run(
                time_step=time_step, number_of_iterations=number_of_iterations
            )
            if n_iteration > n_max_iterations or n_iteration < 0:
                _has_converged = True
                n_non_convergence = n_non_convergence + 1
                non_convergence_times.append(time_step)
            if not iterate:
                _has_converged = True
            if not _has_converged:
                n_iteration = n_iteration + 1
            # _end_iteration(time_step)

    print(f"{air_flow_building.previous_pressures = }")
    print(f"{air_flow_building.pressures = }")
    print(f"{air_flow_building.flow_rates = }")
