# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import json
import numpy
import pathlib
import typing
import time

from matplotlib import pyplot as plt

# ========================================
# Internal imports
# ========================================

from core.link               import Link
from core.model              import Model
from core.plot               import Plot
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
        self._plots = dict()
        self._set_project_parameters()
        self._has_converged = None

    def add(self, model: Model) -> None:
        self.models.append(model)
        model.project = self
        return self

    def get(self, name):
        models = [model for model in self.models if model.name == name]
        if models:
            return models[0]
        return None

    # TODO: Rename get_models_from_class?
    def get_models(self, cls):
        return [model for model in self.models if self.models[0].__class__.__name__ == cls]

    @typing.overload
    def link(self, *args: tuple[Model, str, Model, str]) -> None:
        ...

    @typing.overload
    def link(self, *args: tuple[Model, Model, VariableConnector]) -> None:
        ...

    def link(self, *args: tuple[Model, str, Model, str] | tuple[Model, Model, VariableConnector]) -> None:
        if any([arg for arg in args if isinstance(arg,  VariableConnector)]):
            from_model, to_model, connector = args
            self.link_with_connector(from_model, to_model, connector)
        else:
            from_model, from_variable, to_model, to_variable = args
            self.link_with_variable_names(from_model, from_variable, to_model, to_variable)

    def link_with_connector(self, from_model: Model, to_model: Model, connector: VariableConnector) -> None:
        for from_variable, to_variable in connector.connections:
            self._add_link(from_model, from_variable, to_model, to_variable)

    def link_with_variable_names(self, from_model: Model, from_variable: str, to_model: Model, to_variable: str) -> None:
        self._add_link(from_model, from_variable, to_model, to_variable)

    def _add_link(self, from_model: Model, from_variable: str, to_model: Model, to_variable: str) -> None:
        if not self.is_eligible_link(from_model, from_variable, to_model, to_variable):
            raise ValueError(f"Sorry, but we cannot link {from_model}.{from_variable} to {to_model}.{to_variable}.")
        if not self.is_linked(from_model, from_variable, to_model, to_variable):
            link = Link(from_model, from_variable, to_model, to_variable)
            self.links.append(link)

    def is_eligible_link(self, from_model: Model, from_variable: str, to_model: Model, to_variable: str) -> bool:
        return hasattr(from_model, from_variable) and hasattr(to_model, to_variable)

    def is_linked(self, from_model: Model, from_variable: str, to_model: Model, to_variable: str) -> bool:
        for link in self.links:
            if (link.from_model == from_model) and (link.to_model == to_model) and (link.from_variable == from_variable) and (link.to_variable == to_variable):
                return True
        return False

    def add_plot(self, name: str, model: Model, variable_name: str) -> None:
        plot = Plot(name, model, variable_name)
        if name in self._plots:
            self._plots[name].append(plot)
        else:
            self._plots[name] = [plot]

    def plot(self):
        if self.to_plot and len(self._plots) >= 1:
            figure      = plt.figure()
            disposition = len(self._plots) * 100 + 11
            for title, plots in self._plots.items():
                axis = figure.add_subplot(disposition)
                axis.set_title(title)
                for plot in plots:
                    model    = plot.model
                    variable = model.get_variable(plot.variable_name)
                    series   = getattr(model, variable.name + "_series")
                    axis.plot(series, label = model.name + "." + variable.name)
                    axis.set_ylabel(f"[{variable.unit.value}]")
                axis.legend(loc = "upper right", numpoints = 1)
                disposition += 1
            # Show plot
            plt.show()
            # Adjust everything automatically
            plt.tight_layout()

    def run(self):
        starting_time = time.perf_counter()
        self._initialize_series()
        self._initialize_models()
        # Run the simulation (for each time step)
        for time_step in range(0, self.time_steps):
            if self.verbose:
                print(f"### step {time_step}")
            n_iteration = 1
            self._has_converged = False
            while not self._has_converged:
                if self.verbose:
                    print(f"Iteration {n_iteration}")
                self._has_converged = True
                self._run_models(time_step)
                self._substitute_links_values()
                # check for convergence limit
                if n_iteration > self.n_max_iterations:
                    self._has_converged    = True
                    self.n_non_convergence = self.n_non_convergence + 1
                    self.non_convergence_times.append(time_step)
                self._end_iteration(time_step)
                self._save_model_data(time_step)
                n_iteration = n_iteration + 1
            self._end_time_step(time_step)
        print("Simulation summary")
        print("==================")
        self._end_simulation(time_step)
        print(f"{self.n_non_convergence} timesteps have convergence problems")
        print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")
        self.plot()

    def _initialize_series(self) -> None:
        for model in self.models:
            for variable in model.outputs:
                setattr(model, variable.name + '_series', numpy.ones(self.time_steps))

    def _initialize_models(self) -> None:
        for model in self.models:
            model.initialize()

    def _substitute_links_values(self):
        for link in self.links:
            value_in  = getattr(link.to_model, link.to_variable).value
            value_out = getattr(link.from_model, link.from_variable).value
            setattr(link.to_model, link.to_variable, value_out)
            if self.verbose:
                print(f"Substituting {link.to_model}.{link.to_variable} by {link.from_model}.{link.from_variable} : {value_in} -> {value_out}")
            if self.iterate:
                if (abs(value_out) > self.convergence_tolerance) and (abs(value_out - value_in) > self.convergence_tolerance):
                    self._has_converged = False
                elif value_out == 0:
                    pass
                elif abs(value_in - value_out) / value_out > self.convergence_tolerance:
                    self._has_converged = False

    def _run_models(self, time_step: int) -> None:
        for model in self.models:
            if self.verbose:
                print(f"Computing: {model.name}")
            model.run(time_step)

    def _end_iteration(self, time_step: int) -> None:
        for model in self.models:
            model.iteration_done(time_step)

    def _save_model_data(self, time_step: int) -> None:
        for model in self.models:
            model.save_time_step(time_step)

    def _end_time_step(self, time_step: int) -> None:
        for model in self.models:
            model.timestep_done(time_step)

    def _end_simulation(self, time_step: int) -> None:
        for model in self.models:
            model.simulation_done(time_step)

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
        self.time_steps   = 168
        self.models_order = []
        self.n_max_iterations = 25
        self.n_non_convergence = 0
        self.non_convergence_times = []
        self.convergence_tolerance = 0.01
        self.iterate = True
        self.verbose = False # TODO: implement printing ON/OFF mechanism
        self.to_plot = True
        if self.schema is Schema.RE2020:
            pass

    # Return the string representation of the object
    def __str__(self) -> str:
        """Return the string representation of the object

        Parameters
        ----------

        Returns
        -------
        string_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        string_representation = f"{self.__class__.__name__}()"
        return string_representation

    # Return the object representation as a string
    def __repr__(self) -> str:
        """Return the object representation as a string

        Parameters
        ----------

        Returns
        -------
        object_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        object_representation = self.__str__()
        return object_representation
