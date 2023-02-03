# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import json
import pathlib
import typing
import time
import numpy as np
from matplotlib import pyplot as plt

# ========================================
# Internal imports
# ========================================


from core.link            import Link
from core.model           import Model
from core.plot            import Plot
from core.variable_list   import VariableList
from utils.encorder_utils import NonCyclycEncoder
from utils.enums_utils    import Schema
from utils.files_utils    import write_json_file

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

    def add(self, model: Model) -> None:
        self.models.append(model)
        model.project = self


    def get(self, name):
        models = [m for m in self.models if m.name == name]
        if len(models) == 1:
            return models[0]
        else:
            return None

    def get_models(self, cls):
        return [m for m in self.models if self.models[0].__class__.__name__ == cls]

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

    def is_eligible_link(self, model1, variable1, model2, variable2):
        for link in self.links:
            if link.from_model == model1 and link.to_model == model2 \
                and link.from_variable == variable1 and link.to_variable == variable2:
                return False
        return hasattr(model1, variable1) and hasattr(model2, variable2)

    def add_plot(self, name: str, model: Model, variable_name: str) -> None:
        plot = Plot(name, model, variable_name)
        if name in self._plots:
            self._plots[name].append(plot)
        else:
            self._plots[name] = [plot]

    def plot(self):
        if self.to_plot and len(self._plots) > 1:
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
                    axis.set_ylabel(f"[{variable.unit.name}]")
                axis.legend(loc = "upper right", numpoints = 1)
                disposition += 1
            #plt.legend(handles=[ax1])
            # Show plot
            plt.show()
            # Adjust everything automatically
            plt.tight_layout()

    def initialize_series(self):
        for model in self.models:
            for variable in model.outputs:
                if type(variable) != VariableList:
                    setattr(model, variable.name + '_series', np.ones(self.time_steps))

    def run(self):
        starting_time = time.perf_counter()

        # Initialize models
        self.initialize_series()
        for model in self.models:
            model.initialize()

        # Run the simulation (for each time step)
        for time_step in range(0, self.time_steps):
            if self.verbose: print(f"### step {time_step}")
            n_iteration = 1
            converged = False
            while not converged:
                if self.verbose: print(f"Iteration {n_iteration}")
                converged = True
                for model in self.models:
                    if self.verbose: print(f"Computing: {model.name}")
                    model.run(time_step)

                # substitute vales following links
                for link in self.links:
                    value_in = getattr(link.to_model, link.to_variable).value
                    value_out = getattr(link.from_model, link.from_variable).value
                    setattr(link.to_model, link.to_variable, value_out)
                    if self.verbose: print(f"Substituting {link.to_model}.{link.to_variable} by {link.from_model}.{link.from_variable} : {value_in} -> {value_out}")

                    if self.iterate:
                        if (abs(value_out) > self.convergence_tolerance) and (abs(value_out - value_in) > self.convergence_tolerance):
                            converged = False
                        elif value_out == 0:
                            pass
                        elif abs(value_in - value_out) / value_out > self.convergence_tolerance:
                            converged = False

                # check for convergence limit
                if n_iteration > self.n_max_iterations:
                    converged = True
                    self.n_non_convergence = self.n_non_convergence + 1
                    self.non_convergence_times.append(time_step)

                model.iteration_done(time_step)

                for model in self.models:
                    model.save_time_step(time_step)

                n_iteration = n_iteration + 1

            model.timestep_done(time_step)

        print("Simulation summary")
        print("==================")
        for m in self.models:
            m.simulation_done(time_step)
        print(f"{self.n_non_convergence} timesteps have convergence problems")
        print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")

        self.plot()

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
