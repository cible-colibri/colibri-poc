"""
ProjectOrchestrator class to run a simulation/project.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union

from matplotlib import pyplot as plt
from matplotlib.pyplot import Figure

from colibri.config.constants import (
    ARCHETYPES,
    ATTACHED_TO,
    CATEGORY,
    DESCRIPTION,
    LOGGER,
    MODULE_COLLECTION,
    PARAMETERS,
    PROJECT,
    SERIES_EXTENSION_NAME,
    SIMULATION_PARAMETERS,
    TYPE,
)
from colibri.core.fields import Parameter, SimulationVariable
from colibri.core.link import Link
from colibri.core.project_data import ProjectData
from colibri.interfaces import (
    Archetype,
    BoundaryObject,
    ElementObject,
    StructureObject,
)
from colibri.project_objects import (
    Boundary,
    BoundaryCondition,
    Building,
    LinearJunction,
    Project,
    PunctualJunction,
    Segment,
    Space,
)
from colibri.utils.class_utils import (
    create_class_instance,
    get_class,
)
from colibri.utils.colibri_utils import (
    Attachment,
    turn_format_to_string,
)
from colibri.utils.enums_utils import (
    ColibriObjectTypes,
    Roles,
)
from colibri.utils.exceptions_utils import LinkError
from colibri.utils.plot_utils import Plot

if TYPE_CHECKING:
    from colibri.interfaces.module import Module


@dataclass
class ProjectOrchestrator:
    """Class representing the project orchestrator."""

    name: str = "project-orchestrator-1"
    links: List[Link] = field(default_factory=list)
    post_initialization_links: List[Link] = field(default_factory=list)
    models: List[Module] = field(default_factory=list)
    time_steps: int = 168
    verbose: bool = False
    iterate_for_convergence: bool = False
    maximum_number_of_iterations: int = 10
    # Internal variables
    _has_converged: bool = False
    _non_convergence_time_steps: List[int] = field(default_factory=list)
    _number_of_iterations: int = 1
    _plots: Dict[str, List[Plot]] = field(default_factory=dict)

    def run(self, show_plots: bool = False) -> dict:
        """Run the project (simulation)

        Parameters
        ----------
        show_plots : bool = False
            Show plots at the end

        Returns
        -------
        information : dict
            Information about the project run

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Start counter to keep track of time for performance
        starting_time = time.perf_counter()
        # Pass parameters information (models' values) to connected models
        self._substitute_parameter_links_values()
        self._substitute_parameter_links_values_2()
        # Add a variable series for each output of each model to store results
        # at each time step
        self._initialize_module_output_series()
        # Initialize models (run models' initialize method)
        self._initialize_models()
        # Pass information (models' values) to connected models
        # if required by post-initialization
        #self._substitute_links_values_for_post_initialization()
        # Use post-initialization for models which relies on
        # the initialization of others
        #self._post_initialize_models()
        # Run the simulation (for each time step)
        for time_step in range(0, self.time_steps):
            # Print time step evolution if needed
            if self.verbose:
                LOGGER.info(f"Time step: {time_step}")
            # Set the number of iterations for convergence purposes
            self._number_of_iterations = 1
            # Set convergence to False before starting the convergence process
            self._has_converged = False
            # Iterate until convergence
            while not self._has_converged:
                # Print the iteration number if needed
                if self.verbose:
                    LOGGER.info(f"Iteration: {self._number_of_iterations}")
                self._has_converged = True
                # TODO: Check if it must be before or after
                # run_models (see initial state)
                # Pass information (models' values) to connected models
                self._substitute_links_values(time_step=time_step)
                # Run models (run models' run method)
                self._run_models(
                    time_step=time_step,
                    number_of_iterations=self._number_of_iterations,
                )
                # Check for convergence limit and set self._has_converged
                self._set_convergence(time_step=time_step)
                # Increment the number of iterations for convergence purposes
                self._number_of_iterations += 1
                # End iteration (run models' iteration_done method)
                self._end_iteration(time_step=time_step)
            # Save the model's data for the given time step
            self._save_module_data(time_step=time_step)
            # End time step (run models' end_time_step method)
            self._end_time_step(time_step=time_step)
        # End simulation (run models' end_simulation method)
        self._end_simulation()
        # Show plots if show_plots is set to True
        if show_plots:
            self.plot()
        ending_time: float = time.perf_counter()
        information: dict = {
            "Non convergent timesteps": self._non_convergence_time_steps,
            "Simulation time": f"{(ending_time - starting_time):3.2f} s",
        }
        return information

    def add_model(self, model: Module) -> ProjectOrchestrator:
        """Add a model to the project

        Parameters
        ----------
        model : Module
            Module to add

        Returns
        -------
        self : ProjectOrchestrator
            ProjectOrchestrator itself

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        self.models.append(model)
        model.project = self
        return self

    def get_models_by_class(self, class_name: str) -> List[Module]:
        """Get all models given a class name

        Parameters
        ----------
        class_name : str
            Name of the class of the model

        Returns
        -------
        List[Module]
            List of models with the given a class name

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        return [
            model
            for model in self.models
            if model.__class__.__name__ == class_name
        ]

    def get_module_by_name(self, name: str) -> Union[Module, None]:
        """Get a model given its name

        Parameters
        ----------
        name : str
            Name of the model

        Returns
        -------
        Union[Module, None]
            Module with the given name or None if no model with that name

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        models: List[Module] = [
            model for model in self.models if model.name == name
        ]
        if not models:
            return None
        return models[0]

    def add_plot(
        self, name: str, model: Module, variable_name: str
    ) -> ProjectOrchestrator:
        """Add plot to the project

        Parameters
        ----------
        name : str
            Name of the plot
        model : Module
            Module from which the variable to be plotted is taken
        variable_name : str
            Name of the variable to be plotted

        Returns
        -------
        self : ProjectOrchestrator
            ProjectOrchestrator itself

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        plot: Plot = Plot(name=name, model=model, variable_name=variable_name)
        self._plots.setdefault(name, [])
        self._plots[name].append(plot)

    def plot(self) -> None:
        """Plot all the desired variables

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
        # Plot only if there is at least one variable to be plotted
        if self._plots:
            # Create the figure to add plots onto it
            figure: Figure = plt.figure(figsize=(10, len(self._plots) * 2))
            location: int = len(self._plots) * 100 + 11
            # Create plots and add them to the figure
            for plot in [
                plot for _, plots in self._plots.items() for plot in plots
            ]:
                plot.add_plot_to_figure(figure=figure, location=location)
                location += 1
            # Show plot
            plt.show()
            # Adjust everything automatically
            plt.tight_layout()

    def add_link(
        self,
        from_module: Module,
        from_field: str,
        to_module: Module,
        to_field: str,
    ) -> ProjectOrchestrator:
        self._add_link(
            from_module=from_module,
            from_field=from_field,
            to_module=to_module,
            to_field=to_field,
        )
        return self

    def create_links_automatically(self) -> None:
        """Create links automatically for the project

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
        # Find inputs, outputs and parameters for each model
        inputs: List[Tuple[Type, str]] = [
            (model, input_variable.name)
            for model in self.models
            for input_variable in model.inputs
        ]
        outputs: List[Tuple[Type, str]] = [
            (model, output_variable.name)
            for model in self.models
            for output_variable in model.outputs
        ]
        # Find all output/input combinations
        output_input_combinations: List[Tuple[str, str]] = list(
            itertools.product(*[outputs, inputs])
        )
        for output_input_combination in output_input_combinations:
            output_module_variable, input_module_variable = (
                output_input_combination
            )
            output_model, output_variable = output_module_variable
            input_model, input_variable = input_module_variable
            is_same_variable: bool = output_variable == input_variable
            is_different_model: bool = output_model != input_model
            if is_same_variable and is_different_model:
                self.add_link(
                    output_model,
                    output_variable,
                    input_model,
                    input_variable,
                )
                if self.verbose is True:
                    LOGGER.info(
                        f"Link {output_model.name}.{output_variable} to {input_model.name}.{input_variable}"
                    )

    @classmethod
    def generate_scheme(cls, modules: List[str]) -> Dict[str, Any]:
        """Generate the COLIBRI's scheme for the given modules

        Parameters
        ----------
        modules : List[str]
            List of modules for the project

        Returns
        -------
        scheme : Dict[str, Any]
            Scheme of the project

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Define categories
        archetype_category: str = Archetype.__name__
        element_object_category: str = ElementObject.__name__
        boundary_object_category: str = BoundaryObject.__name__
        structure_object_category: str = StructureObject.__name__
        module_category: str = "Modules"
        # Define schemes
        archetype_scheme: Dict[str, Any] = Archetype.to_scheme()[
            archetype_category
        ]
        boundary_object_scheme: Dict[str, Any] = BoundaryObject.to_scheme()[
            boundary_object_category
        ]
        element_object_scheme: Dict[str, Any] = ElementObject.to_scheme()
        # Define the final scheme
        scheme: Dict[str, Dict[str, Any]] = {
            archetype_category: dict(),
            boundary_object_category: dict(),
            element_object_category: dict(),
            module_category: dict(),
            structure_object_category: dict(),
        }
        # Set all parameters that are mandatory for project objects
        cls._set_project_objects_base_scheme(
            scheme=scheme, structure_object_category=structure_object_category
        )
        # For each module
        for module_name in modules:
            module: Type = get_class(
                class_name=module_name,
                output_type=ColibriObjectTypes.MODULE,
            )
            module_scheme: Dict[str, Dict[str, Any]] = module.to_scheme()
            for scheme_name, scheme_group in module_scheme.items():
                # Archetypes
                if scheme_name == ARCHETYPES.capitalize():
                    cls._set_archetypes_scheme(
                        scheme,
                        scheme_group,
                        archetype_category,
                        archetype_scheme,
                    )
                scheme_category: str = scheme_group.pop(CATEGORY, None)
                # Boundary objects
                if (
                    scheme_name not in scheme
                ) and scheme_category == boundary_object_category:
                    cls._set_base_boundary_objects_scheme(
                        scheme,
                        scheme_group,
                        boundary_object_category,
                        scheme_name,
                        boundary_object_scheme,
                    )
                # Element objects
                if scheme_name == element_object_category:
                    cls._set_base_element_objects_scheme(
                        scheme,
                        scheme_group,
                        element_object_category,
                        element_object_scheme,
                        boundary_object_scheme,
                        archetype_category,
                        archetype_scheme,
                    )
                # Module and structure objects
                if scheme_name != ARCHETYPES.capitalize():
                    cls._set_module_objects_scheme(
                        scheme,
                        scheme_group,
                        scheme_name,
                        scheme_category,
                        modules,
                        boundary_object_category,
                        element_object_category,
                        structure_object_category,
                        module_category,
                    )
        return scheme

    @classmethod
    def _set_project_objects_base_scheme(
        cls, scheme: Dict[str, Dict[str, Any]], structure_object_category: str
    ) -> None:
        for project_object_class in [
            Boundary,
            BoundaryCondition,
            Building,
            LinearJunction,
            PunctualJunction,
            Project,
            Segment,
            Space,
        ]:
            temporary_class_name: str = project_object_class.__name__
            temporary_scheme: Dict[str, Any] = project_object_class.to_scheme()
            scheme[structure_object_category][temporary_class_name] = {
                TYPE: temporary_scheme[temporary_class_name].pop(TYPE, None),
                DESCRIPTION: temporary_scheme[temporary_class_name].pop(
                    DESCRIPTION, None
                ),
                PARAMETERS: temporary_scheme[temporary_class_name],
            }

    @classmethod
    def _set_archetypes_scheme(
        cls, scheme, scheme_group, archetype_category, archetype_scheme
    ):
        scheme.setdefault(archetype_category, dict())
        for archetype_name, archetype_data in scheme_group.items():
            _ = archetype_data.pop(CATEGORY, None)
            if archetype_name not in scheme[archetype_category]:
                scheme[archetype_category].setdefault(
                    archetype_name,
                    {
                        DESCRIPTION: archetype_scheme.pop(DESCRIPTION, None),
                        PARAMETERS: dict(),
                        TYPE: archetype_scheme.pop(TYPE, None),
                    },
                )
                for (
                    parameter_name,
                    parameter_data,
                ) in archetype_scheme.items():
                    scheme[archetype_category][archetype_name][PARAMETERS][
                        parameter_name
                    ] = parameter_data
            for (
                parameter_name,
                parameter_data,
            ) in archetype_data.items():
                scheme[archetype_category][archetype_name][PARAMETERS][
                    parameter_name
                ] = parameter_data

    @classmethod
    def _set_base_boundary_objects_scheme(
        cls,
        scheme,
        scheme_group,
        boundary_object_category,
        scheme_name,
        boundary_object_scheme,
    ):
        scheme[boundary_object_category].setdefault(
            scheme_name,
            {
                DESCRIPTION: boundary_object_scheme.pop(DESCRIPTION, None),
                PARAMETERS: dict(),
                TYPE: boundary_object_scheme.pop(TYPE, None),
            },
        )
        for (
            parameter_name,
            parameter_data,
        ) in boundary_object_scheme.items():
            scheme[boundary_object_category][scheme_name][PARAMETERS][
                parameter_name
            ] = parameter_data

    @classmethod
    def _set_base_element_objects_scheme(
        cls,
        scheme,
        scheme_group,
        element_object_category,
        element_object_scheme,
        boundary_object_scheme,
        archetype_category,
        archetype_scheme,
    ):
        element_object_archetype_name: str = next(iter(scheme_group))
        scheme_category: str = scheme_group[element_object_archetype_name].pop(
            CATEGORY, None
        )
        attached_to: str = scheme_group[element_object_archetype_name].pop(
            ATTACHED_TO, None
        )
        element_object_name: str = next(
            iter(scheme_group[element_object_archetype_name])
        )
        scheme[element_object_category].setdefault(
            element_object_name,
            {
                DESCRIPTION: scheme_group[element_object_archetype_name][
                    element_object_name
                ].pop(DESCRIPTION, None),
                PARAMETERS: dict(),
                TYPE: element_object_scheme.pop(
                    TYPE, element_object_archetype_name
                ),
                ATTACHED_TO: attached_to,
            },
        )
        scheme[scheme_category].setdefault(
            attached_to, {DESCRIPTION: None, PARAMETERS: dict(), TYPE: None}
        )
        scheme[scheme_category][attached_to][PARAMETERS].setdefault(
            element_object_name, dict()
        )
        parameters: dict = scheme_group[element_object_archetype_name][
            element_object_name
        ]
        _ = scheme_group[element_object_archetype_name][
            element_object_name
        ].pop("required", None)
        if DESCRIPTION not in parameters:
            parameters[DESCRIPTION] = None
        scheme[scheme_category][attached_to][PARAMETERS][
            element_object_name
        ] = scheme_group[element_object_archetype_name][element_object_name]

        """
        for (
            parameter_name,
            parameter_data,
        ) in boundary_object_scheme.items():
            scheme[element_object_category][element_object_name][PARAMETERS][
                parameter_name
            ] = parameter_data
        """
        # TODO: Factorize with archetype objects
        if attached_to not in scheme[archetype_category]:
            scheme[archetype_category].setdefault(
                attached_to,
                {
                    DESCRIPTION: archetype_scheme.pop(DESCRIPTION, None),
                    PARAMETERS: dict(),
                    TYPE: archetype_scheme.pop(TYPE, None),
                },
            )
            for (
                parameter_name,
                parameter_data,
            ) in archetype_scheme.items():
                scheme[archetype_category][attached_to][PARAMETERS][
                    parameter_name
                ] = parameter_data

    @classmethod
    def _set_module_objects_scheme(
        clas,
        scheme,
        scheme_group,
        scheme_name,
        scheme_category,
        modules,
        boundary_object_category,
        element_object_category,
        structure_object_category,
        module_category,
    ):
        # Modules' parameters
        if scheme_name in modules:
            for (
                parameter_name,
                parameter_data,
            ) in scheme_group.items():
                scheme[module_category].setdefault(
                    scheme_name,
                    {
                        DESCRIPTION: None,
                        PARAMETERS: dict(),
                        TYPE: None,
                    },
                )
                scheme[module_category][scheme_name][PARAMETERS][
                    parameter_name
                ] = parameter_data
        # Structured and boundary objects' parameters
        if (scheme_name not in modules) and (
            scheme_name != element_object_category
        ):
            category: str = (
                boundary_object_category
                if scheme_category == boundary_object_category
                else structure_object_category
            )
            for (
                parameter_name,
                parameter_data,
            ) in scheme_group.items():
                scheme[category].setdefault(
                    scheme_name,
                    {
                        DESCRIPTION: None,
                        PARAMETERS: dict(),
                        TYPE: None,
                    },
                )
                scheme[category][scheme_name][PARAMETERS][parameter_name] = (
                    parameter_data
                )

    # TODO: To be finished
    @classmethod
    def create_project(
        cls, project_data: Dict[str, Any]
    ) -> ProjectOrchestrator:
        project_name: str = project_data[PROJECT].get("id", "project-1")
        simulation_parameters: dict = project_data[PROJECT][
            SIMULATION_PARAMETERS
        ]
        parameters: dict = {"name": project_name} | simulation_parameters
        project: ProjectOrchestrator = cls(**parameters)
        """
        project_data: ProjectData = ProjectData(
            name="project-data-1", data=project_data
        )
        project.add_model(model=project_data)
        """
        for module_name in project_data[PROJECT][MODULE_COLLECTION]:
            module_instance: Module = create_class_instance(
                class_name=module_name,
                class_parameters=dict(),
                output_type=ColibriObjectTypes.MODULE,
            )
            project.add_model(model=module_instance)
        project.create_links_automatically()
        return project

    def _add_link(
        self,
        from_module: Module,
        from_field: str,
        to_module: Module,
        to_field: str,
    ) -> None:
        if to_module.is_field_linked(field_name=to_field):
            link: Link = to_module.get_link(field_name=to_field)
            existing_link: str = f"{link.from_module.name}.{link.from_field}"
            raise LinkError(
                f"Cannot link {from_module.name}.{from_field} "
                f"to {to_module.name}.{to_field}, because "
                f"{to_module.name}.{to_field} is already linked to "
                f"{existing_link}."
            )
        link: Link = Link(
            from_module=from_module,
            from_field=from_field,
            to_module=to_module,
            to_field=to_field,
        )
        self.links.append(link)

    def _substitute_parameter_links_values(self):
        """"""
        for link in self.links:
            if link.to_module.get_field(link.to_field).role is Roles.PARAMETERS:
                from_field = getattr(link.from_module, link.from_field)
                setattr(link.to_module, link.to_field, from_field)

    def _substitute_parameter_links_values_2(self):
        for module in self.models:
            parameters: List[Parameter] = module.parameters
            for parameter in parameters:
                parameter_format: str = turn_format_to_string(
                    field_format=parameter.format
                )
                if parameter_format == "ProjectData":
                    project_data: Module = self.get_models_by_class(
                        class_name="ProjectData"
                    )[0]
                    setattr(module, parameter.name, project_data)

    def _initialize_module_output_series(self) -> None:
        """Create a variable for each output of each model to store results at
         each time step

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
        for model in self.models:
            for variable in model.outputs:
                serie_name: str = f"{variable.name}{SERIES_EXTENSION_NAME}"
                setattr(model, serie_name, [0] * self.time_steps)

    def _initialize_models(self) -> None:
        """Run the initialize method of each model in the project
        re-try until all models are initialized to solve dependencies between models

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
        done : bool = False
        max_iterations = 3

        i = 0
        while not done and i < max_iterations:
            all_done = True
            for model in self.models:
                if not model.is_initialized:
                    model_done = model.initialize()
                    if not model_done:
                        all_done = False
                    else:
                        model.is_initialized = True
            self._substitute_links_values(0)
            done = all_done
            i = i + 1

    def _post_initialize_models(self) -> None:
        """Run the post_initialize method of each model in the project

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
        for model in self.models:
            model.post_initialize()

    def _run_models(self, time_step: int, number_of_iterations: int) -> None:
        """Run the run method of each model in the project

        Parameters
        ----------
        time_step : int
            Current time step of the simulation
        number_of_iterations : int
            Number of iterations within the current time step

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
        for model in self.models:
            if self.verbose:
                LOGGER.info(f"Computing: {model.name}")
            model.run(
                time_step=time_step,
                number_of_iterations=number_of_iterations,
            )

    def _substitute_links_values(self, time_step: int) -> None:
        """Pass information (models' values) to connected models
        by substituting the output links' value to the input links' value

        Parameters
        ----------
        time_step : int
            Current time step of the simulation

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
        for link in self.links:
            new_value: Any = getattr(link.from_module, link.from_field)
            setattr(link.to_module, link.to_field, new_value)

    def _substitute_links_values_for_post_initialization(self) -> None:
        """Pass information (models' values) to connected models
        by substituting the output links' value to the input links' value
        only on simulation variables which have use_post_initialization
        set to True

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
        for link in self.post_initialization_links:
            new_value: Any = getattr(link.from_module, link.from_field)
            setattr(link.to_module, link.to_field, new_value)

    def _set_convergence(self, time_step: int) -> None:
        """Set convergence to True if iteration threshold has been reached or
         if no iteration should be performed (iterate_for_convergence = False)
         to break convergence cycle

        Parameters
        ----------
        time_step : int
            Current time step of the simulation

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
        if self.iterate_for_convergence is False:
            self._has_converged = True
        if self._number_of_iterations > self.maximum_number_of_iterations:
            self._has_converged = True
            self._non_convergence_time_steps.append(time_step)

    def _end_iteration(self, time_step: int) -> None:
        """Run the end_iteration method of each model in the project

        Parameters
        ----------
        time_step : int
            Current time step of the simulation

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
        for model in self.models:
            model.end_iteration(time_step=time_step)

    def _save_module_data(self, time_step: int) -> None:
        """Run the save_time_step method of each model in the project

        Parameters
        ----------
        time_step : int
            Current time step of the simulation

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
        for model in self.models:
            model.save_time_step(time_step=time_step)

    def _end_time_step(self, time_step: int) -> None:
        """Run the end_time_step method of each model in the project

        Parameters
        ----------
        time_step : int
            Current time step of the simulation

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
        for model in self.models:
            model.end_time_step(time_step=time_step)

    def _end_simulation(self) -> None:
        """Run the end_simulation method of each model in the project

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
        for model in self.models:
            model.end_simulation()


if __name__ == "__main__":

    def test_project_creation() -> None:
        # Create project
        project_data: dict = {
            "project": {
                "id": "project-12",
                "simulation_parameters": {
                    "time_steps": 48,
                    "verbose": False,
                    "iterate_for_convergence": True,
                    "maximum_number_of_iterations": 10,
                },
                "module_collection": {
                    "AcvExploitationOnly": {},
                    "LimitedGenerator": {},
                    "OccupantModel": {},
                    "SimplifiedWallLosses": {},
                    "ThermalSpaceSimplified": {},
                    "WeatherModel": {},
                },
            },
        }
        project: ProjectOrchestrator = ProjectOrchestrator.create_project(
            project_data=project_data
        )
        print(project)
        # project.run()

    def test_links() -> None:
        from pathlib import Path

        from colibri.core.project_data import ProjectData
        from colibri.modules import (
            AcvExploitationOnly,
            InfinitePowerGenerator,
            LayerWallLosses,
            LimitedGenerator,
            OccupantModel,
            SimplifiedWallLosses,
            ThermalSpaceSimplified,
            WeatherModel,
        )

        # Create project
        project: ProjectOrchestrator = ProjectOrchestrator(
            name="my-project",
            verbose=False,
            time_steps=72,
        )

        # Create models
        project_file: Path = Path(
            r"D:\developments\sandbox\colibri\src\tests\data\house_1.json"
        )
        project_data: ProjectData = ProjectData(
            name="project_data", data=project_file
        )

        acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(
            name="acv"
        )
        infinite_power_generator: InfinitePowerGenerator = (
            InfinitePowerGenerator(name="infinite_power_generator")
        )
        LOGGER.info(infinite_power_generator)
        limited_power_generator: LimitedGenerator = LimitedGenerator(
            name="limited_power_generator"
        )
        simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
            name="simplified_wall_losses"
        )
        thermal_space_simplified: ThermalSpaceSimplified = (
            ThermalSpaceSimplified(name="thermal_space_simplified")
        )
        layer_wall_losses: LayerWallLosses = LayerWallLosses(
            name="layer_wall_losses"
        )
        LOGGER.info(layer_wall_losses)
        occupants: OccupantModel = OccupantModel(name="occupants")
        weather: WeatherModel = WeatherModel(
            name="weather",
            scenario_exterior_air_temperatures=[
                16,
                11,
                18,
                15,
                6,
                10,
                14,
                17,
                13,
                14,
                7,
                15,
                19,
                7,
                18,
                13,
                12,
                18,
                5,
                19,
                19,
                5,
                9,
                6,
                10,
                10,
                16,
                18,
                11,
                19,
                5,
                19,
                18,
                11,
                17,
                18,
                11,
                14,
                13,
                11,
                13,
                16,
                17,
                17,
                16,
                16,
                19,
                9,
                17,
                12,
                19,
                19,
                19,
                19,
                18,
                11,
                6,
                5,
                7,
                17,
                17,
                15,
                12,
                15,
                5,
                15,
                10,
                18,
                12,
                14,
                20,
                6,
            ],
        )

        # Add models
        project.add_model(model=project_data)
        project.add_model(model=acv_exploitation_only)
        project.add_model(
            model=limited_power_generator,  # infinite_power_generator
        )  # limited_power_generator)
        project.add_model(model=layer_wall_losses)  # simplified_wall_losses)
        project.add_model(model=thermal_space_simplified)
        project.add_model(model=occupants)
        project.add_model(model=weather)

        # Add links
        project.create_links_automatically()

        """
        project.add_link(
            project_data, "boundaries", simplified_wall_losses, "boundaries"
        )
        project.add_link(project_data, "spaces", thermal_space_simplified, "spaces")
        project.add_link(
            project_data, "spaces", infinite_power_generator, "spaces"
        )  # limited_power_generator, "spaces")
        project.add_link(project_data, "spaces", occupants, "spaces")
        project.add_link(
            weather,
            "exterior_air_temperature",
            simplified_wall_losses,
            "exterior_air_temperature",
        )
        project.add_link(
            thermal_space_simplified,
            "inside_air_temperatures",
            simplified_wall_losses,
            "inside_air_temperatures",
        )
        project.add_link(
            simplified_wall_losses, "q_walls", thermal_space_simplified, "q_walls"
        )
        project.add_link(
            thermal_space_simplified,
            "q_needs",
            infinite_power_generator,
            "q_needs",  # limited_power_generator, "q_needs"
        )
        project.add_link(
            infinite_power_generator,  # limited_power_generator,
            "q_provided",
            thermal_space_simplified,
            "q_provided",
        )
        project.add_link(
            infinite_power_generator,  # limited_power_generator,
            "q_consumed",
            acv_exploitation_only,
            "q_consumed",
        )
        project.add_link(
            occupants,
            "setpoint_temperatures",
            thermal_space_simplified,
            "setpoint_temperatures",
        )
        project.add_link(occupants, "gains", thermal_space_simplified, "gains")
        """

        # Add plots
        project.add_plot("Weather", weather, "exterior_air_temperature")
        project.add_plot(
            "Tint", thermal_space_simplified, "inside_air_temperatures"
        )
        project.add_plot(
            "Qwall", layer_wall_losses, "q_walls"
        )  # simplified_wall_losses, "q_walls")
        project.add_plot(
            "Qprovided", limited_power_generator, "q_provided"
        )  # limited_power_generator, "q_provided")

        # Run project
        project.run()

        # Plots
        project.plot()

    def test_scheme_creation() -> None:
        import json

        module_collection: List[str] = [
            "AcvExploitationOnly",
            "LimitedGenerator",
            "OccupantModel",
            "LayerWallLosses",
            "ThermalSpaceSimplified",
            "WeatherModel",
        ]
        scheme = ProjectOrchestrator.generate_scheme(modules=module_collection)
        print(json.dumps(scheme, indent=2))
        with open("toto.json", "w") as _f:
            json.dump(scheme, _f, indent=2)

    # test_scheme_creation()
    test_links()
    # from colibri.modules import LayerWallLosses
    # print(LayerWallLosses.to_scheme()["ElementObject"])
