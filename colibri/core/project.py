# ========================================
# External imports
# ========================================

import json

import pathlib
import typing
import time

import numpy as np
from matplotlib import pyplot as plt

from colibri.core.Building import Building
# ========================================
# Internal imports
# ========================================

from colibri.core.helpers.link import Link
from colibri.core.model              import Model
from colibri.core.helpers.plot import Plot
from colibri.core.variables.variable_connector import VariableConnector
from colibri.core.helpers.building.building_data import BuildingData
from colibri.models.utility.weather import Weather
from colibri.utils.encorder_utils import NonCyclycEncoder
from colibri.utils.enums_utils import Schema
from colibri.utils.files_utils import write_json_file

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
        self.time_step = 0
        self.n_iteration = 0

    def add(self, model: Model) -> None:
        self.models.append(model)
        model.project = self
        return self

    def get(self, name):
        models = [model for model in self.models if model.name == name]
        if models:
            return models[0]
        return None

    def get_models_from_class(self, cls):
        return [model for model in self.models if isinstance(model, cls)]

    def get_model_by_name(self, name):
        return [model for model in self.models if model.name == name]

    def get_weather(self):
        weather_models = self.get_models_from_class(Weather)
        if len(weather_models) == 1:
            return weather_models[0]
        elif len(weather_models) > 1:
            raise Exception("More than one weather model in project, don't know which one to choose.")
        else:
            raise Exception("No weather model in project, but some models need one.")

    def get_building_data(self):
        data_models = self.get_models_from_class(BuildingData)
        if len(data_models) == 1:
            return data_models[0]
        elif len(data_models) > 1:
            raise Exception("More than one datar model in project, don't know which one to choose.")
        else:
            raise Exception("No data model in project, but some models need one.")

    #@typing.overload
    #def link(self, *args: tuple[Model, str, Model, str]) -> None:
    #    ...

    #@typing.overload
    #def link(self, *args: tuple[Model, Model, VariableConnector]) -> None:
    #    ...

    def link(self, model_1, arg_2, *connection):
        if len(connection) ==2:
            model_2 = connection[0]
            variable_2 = connection[1]
            if not self.is_eligible_link(model_1, arg_2, model_2, variable_2):
                raise ValueError(f"Cannot link {model_1}.{arg_2} to {model_2}.{variable_2}")
            link = Link(model_1, arg_2, model_2, variable_2)
            self.links.append(link)
        else:
            connector = connection[0]
            for c in connector.connections:
                if not self.is_eligible_link(model_1, c[0], arg_2, c[1]):
                    raise ValueError(f"Cannot link {model_1}.{c[0]} to {arg_2}.{c[1]}")
                link = Link(model_1, c[0], arg_2, c[1])
                self.links.append(link)

    def link_to_vector(self, model_1, var_1, model_2, var_2, index_2):
        if not self.is_eligible_link(model_1, var_1, model_2, var_2):
            raise ValueError(f"Cannot link {model_1}.{var_2} to {model_2}.{var_2}")
        link = Link(model_1, var_1, model_2, var_2, None, index_2)
        self.links.append(link)

    def link_from_vector(self, model_1, var_1, index_1, model_2, var_2):
        if not self.is_eligible_link(model_1, var_1, model_2, var_2):
            raise ValueError(f"Cannot link {model_1}.{var_2} to {model_2}.{var_2}")
        link = Link(model_1, var_1, model_2, var_2, index_1, None)
        self.links.append(link)

    def link_vector_to_vector(self, model_1, var_1, index_1, model_2, var_2, index_2):
        if not self.is_eligible_link(model_1, var_1, model_2, var_2):
            raise ValueError(f"Cannot link {model_1}.{var_2} to {model_2}.{var_2}")
        link = Link(model_1, var_1, model_2, var_2, index_1, index_2)
        self.links.append(link)

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
        result = hasattr(from_model, from_variable) and hasattr(to_model, to_variable)
        return result

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
                    field = model.get_field(plot.variable_name)
                    if not field: # to be removed with Variables
                        field = model.get_variable(plot.variable_name)
                    series   = getattr(model, field.name + "_series")
                    axis.plot(series, label = model.name + "." + field.name)
                    axis.set_ylabel(f"[{field.unit}]")
                axis.legend(loc = "upper right", numpoints = 1)
                disposition += 1
            # Show plot
            plt.show()
            # Adjust everything automatically
            plt.tight_layout()

    def run(self, show_plot: bool = False):
        starting_time = time.perf_counter()
        self._initialize_series()
        self._initialize_models()
        # Run the simulation (for each time step)
        for self.time_step in range(0, self.time_steps):
            if self.verbose:
                print(f"### step {self.time_step}")
            self.n_iteration = 1
            self._has_converged = False
            while not self._has_converged:
                if self.verbose:
                    print(f"Iteration {self.n_iteration}")
                self._has_converged = True
                self._run_models(self.time_step, self.n_iteration)
                self._substitute_links_values()
                # check for convergence limit
                if self.n_iteration > self.n_max_iterations:
                    self._has_converged    = True
                    self.n_non_convergence = self.n_non_convergence + 1
                    self.non_convergence_times.append(self.time_step)
                self.n_iteration = self.n_iteration + 1
                if not self.iterate:
                    self._has_converged = True
                self._end_iteration(self.time_step)
            self._save_model_data(self.time_step)
            self._end_time_step(self.time_step)
        print("Simulation summary")
        print("==================")
        self._end_simulation(self.time_step)
        self.runtime = (time.perf_counter() - starting_time)
        print(f"{self.n_non_convergence} timesteps have convergence problems")
        print(f"Simulation time: {self.runtime:3.2f} seconds")
        if show_plot is True:
            self.plot()

    def _initialize_series(self) -> None:
        for model in self.models:
            for variable in model.get_output_fields():
                setattr(model, variable.name + '_series', [0] * self.time_steps)
            for field in model.get_output_fields():
                setattr(model, field.name + '_series', [0] * self.time_steps)

    def _initialize_models(self) -> None:
        for model in self.models:
            model.initialize()

    def _substitute_links_values(self):
        for link in self.links:
            if link.index_to is None:
                to_variable = getattr(link.to_model, link.to_variable)
                if hasattr(to_variable, 'value'):
                    value_in = to_variable # link to a scalar Variable
                else:
                    value_in = to_variable # link to a scalar Field
            else:
                value_in = getattr(link.to_model, link.to_variable)[link.index_from] # link to a vector

            if link.index_from is None:
                from_variable = getattr(link.from_model, link.from_variable)
                if hasattr(from_variable, 'value'):
                    value_out = from_variable # link from a scalar Variable
                else:
                    value_out = from_variable  # link from a scalar Field
            else:
                value_out = getattr(link.from_model, link.from_variable)[link.index_from] # link from a vector

            if link.index_to is None or isinstance(value_out, dict):
                to_variable = getattr(link.to_model, link.to_variable)
                if hasattr(to_variable, 'value'):
                    to_variable = value_out # link dict to Variable
                else:
                    setattr(link.to_model, link.to_variable, value_out)  # link dict to field
            else:
                target_var = getattr(link.to_model, link.to_variable) # TODO: test ; or remove everything Variable / value-ish
                if target_var.size < link.index_to + 1:
                    target_var = np.resize(target_var, link.index_to + 1) # resize target vector
                value_in = target_var[link.index_to]
                target_var[link.index_to] = value_out

            if self.verbose:
                print(f"Substituting {link.to_model}.{link.to_variable} by {link.from_model}.{link.from_variable} : {value_in} -> {value_out}")
            from_model_converged = link.from_model.converged(self.time_step, self.n_iteration)
            to_model_converged = link.to_model.converged(self.time_step, self.n_iteration)
            if (not to_model_converged is None and not to_model_converged):
                self._has_converged = False
            elif (not from_model_converged is None and not from_model_converged):
                    self._has_converged = False
            elif self.iterate and not ((hasattr(value_out, '__len__') or hasattr(value_in, '__len__')) or isinstance(value_out, dict) or isinstance(value_in, dict)):
                if (abs(value_out) > self.convergence_tolerance) and (abs(value_out - value_in) > self.convergence_tolerance):
                    self._has_converged = False
                elif value_out == 0:
                    pass
                elif abs(value_in - value_out) / value_out > self.convergence_tolerance:
                    self._has_converged = False

    def _run_models(self, time_step: int, n_iteration: int) -> None:
        for model in self.models:
            if self.verbose:
                print(f"Computing: {model.name}")
            model.run(time_step, n_iteration)

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

    def create_envelop(self):
        for building in self.get_models_from_class(Building):
            building.create_envelop()

    def create_systems(self):
        for building in self.get_models_from_class(Building):
            building.create_systems()
