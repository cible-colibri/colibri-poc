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

    def link(self, model_1: Model, model_2: Model, connector: VariableConnector):
        for connection_from, connection_to in connector.connections:
            link = Link(model_1, connection_from, model_2, connection_to)
            self.links.append(link)

    def run(self):
        # Initialize models
        for model in self.models:
            model.initialize()

        # Run the simulation (for each time step)
        for time_step in range(0, self.time_steps):
            for i in range(2):
                print("Iteration ", i)
                for model in self.models:
                    print(f"Computing: {model.name}")
                    model.run()
                for link in self.links:
                    print(f"Substituting {link.from_model}.{link.from_variable} by {link.to_model}.{link.to_variable}")
                m.iteration_done()

        for m in self.models:
            m.simulation_done()
        print("Result is 42.")

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