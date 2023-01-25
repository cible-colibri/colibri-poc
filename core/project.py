# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import json
import pathlib
import typing

# ========================================
# Internal imports
# ========================================

from core.link               import Link
from core.model              import Model
from core.variable_connector import VariableConnector
from utils.encorder_utils    import NonCyclycEncoder
from utils.enums_utils       import Schema
from utils.files_utils       import write_json_file

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class Project:

    def __init__(self, name: str = None, schema: Schema = Schema.RE2020):
        self.name   = name
        self.schema = schema
        self.models = []
        self.links  = []
        self._set_project_parameters()

    def add(self, model: Model) -> None:
        self.models.append(model)

    def get(self, name):
        models = [m for m in self.models if m.name == name]
        if len(models) == 1:
            return models[0]
        else:
            return None

    def link(self, model_1, arg_2, *connection):
        if len(connection) ==2:
            model_2 = connection[0]
            variable_2 = connection[1]
            link = Link(model_1, arg_2, model_2, variable_2)
            self.links.append(link)
        else:
            connector = connection[0]
            for c in connector.connections:
                link = Link(model_1, c[0], arg_2, c[1])
                self.links.append(link)

    def run(self):
        # Initialize models
        for model in self.models:
            model.initialize()

        # Run the simulation (for each time step)
        for time_step in range(0, self.time_steps):
            n_iteration = 1
            converged = False
            while not converged:
                print(f"Iteration {n_iteration}")
                for model in self.models:
                    print(f"Computing: {model.name}")
                    model.run()

                    # substitute vales following links
                    for link in self.links:
                        value_in = getattr(link.from_model, link.to_variable)
                        value_out = getattr(link.from_model, link.from_variable)
                        setattr(link.to_model, link.to_variable, value_out)
                        print(f"Substituting {link.from_model}.{link.from_variable} by {link.to_model}.{link.to_variable} : {value_out} -> {value_out}")

                        if (abs(value_out) < self.convergence_tolerance) and (abs(value_out - value_in) < self.convergence_tolerance):
                            converged = True
                        elif value_out == 0:
                            pass
                        elif abs(value_in - value_out) / value_out < self.convergence_tolerance:
                            converged = True

                # check for convergence limit
                if n_iteration > self.n_max_iterations:
                    converged = True
                    self.n_non_convergence = self.n_non_convergence + 1
                    self.non_convergence_times.append(time_step)

                model.iteration_done()
                n_iteration = n_iteration + 1

            model.timestep_done()

        print("Simulation summary")
        print("==================")
        for m in self.models:
            m.simulation_done()
        print(f"{self.n_non_convergence} timesteps have convergence problems")

    # Return project as json object
    def to_json(self) -> str:
        """Return project as json object

        Parameters
        ----------

        Returns
        -------
        str
            Project as json objecty

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        return json.dumps(self, cls = NonCyclycEncoder, check_circular = False, indent = 2)

    # Save project as a json file
    def save_as_json(self, file_path: typing.Union[str, pathlib.Path]) -> None:
        """Save project as a json file

        Parameters
        ----------
        file_path : typing.Union[str, pathlib.Path]
            Path to the where the project will be saved

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
        write_json_file(file_path, self.to_json())

    def _set_project_parameters(self) -> None:
        if self.schema is Schema.RE2020:
            self.time_steps   = 24
            self.models_order = []
            self.n_max_iterations = 5
            self.n_non_convergence = 0
            self.non_convergence_times = []
            self.convergence_tolerance = 0.01
