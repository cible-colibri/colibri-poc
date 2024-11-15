"""
ProjectOrchestrator class to run a simulation/project.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Set, Tuple, Type, Union

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
from colibri.utils.exceptions_utils import InitializationError, LinkError
from colibri.utils.plot_utils import Plot

if TYPE_CHECKING:
    from colibri.interfaces.module import Module


@dataclass
class ProjectOrchestrator:
    """Class representing the project orchestrator."""

    name: str = "project-orchestrator-1"
    links: List[Link] = field(default_factory=list)
    modules: List[Module] = field(default_factory=list)
    time_steps: int = 168
    verbose: bool = False
    iterate_for_convergence: bool = False
    maximum_number_of_iterations: int = 10
    project_data: ProjectData = None
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
        # Set the simulation parameters
        self._set_simulation_parameters()
        # Pass parameters information (modules' values) to connected modules
        self._substitute_parameter_links_values()
        # Pass project data's information to each module that needs information from the project data
        self._pass_project_data_information_to_modules()
        # Set the value for each intrinsic parameter (defined at the module level) of each module
        self._set_intrinsic_modules_parameters_value()
        # Add a variable series for each output of each module to store results
        # at each time step
        self._initialize_module_output_series()
        # Initialize modules (run modules' initialize method)
        self._initialize_modules()
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
                # run_modules (see initial state)
                # Pass information (modules' values) to connected modules
                self._substitute_links_values()
                # Run modules (run modules' run method)
                self._run_modules(
                    time_step=time_step,
                    number_of_iterations=self._number_of_iterations,
                )
                # Check for convergence limit and set self._has_converged
                self._set_convergence(time_step=time_step)
                # Increment the number of iterations for convergence purposes
                self._number_of_iterations += 1
                # End iteration (run modules' iteration_done method)
                self._end_iteration(time_step=time_step)
            # Save the module's data for the given time step
            self._save_module_data(time_step=time_step)
            # End time step (run modules' end_time_step method)
            self._end_time_step(time_step=time_step)
        # End simulation (run modules' end_simulation method)
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

    def add_module(self, module: Module) -> ProjectOrchestrator:
        """Add a module to the project

        Parameters
        ----------
        module : Module
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
        self.modules.append(module)
        module.project = self
        if isinstance(module, ProjectData) is True:
            self.project_data = module
        return self

    def get_modules_by_class(self, class_name: str) -> List[Module]:
        """Get all modules given a class name

        Parameters
        ----------
        class_name : str
            Name of the class of the module

        Returns
        -------
        List[Module]
            List of modules with the given a class name

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        return [
            module
            for module in self.modules
            if module.__class__.__name__ == class_name
        ]

    def get_module_by_name(self, name: str) -> Union[Module, None]:
        """Get a module given its name

        Parameters
        ----------
        name : str
            Name of the module

        Returns
        -------
        Union[Module, None]
            Module with the given name or None if no module with that name

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        modules: List[Module] = [
            module for module in self.modules if module.name == name
        ]
        if not modules:
            return None
        return modules[0]

    def add_plot(
        self, name: str, module: Module, variable_name: str
    ) -> ProjectOrchestrator:
        """Add plot to the project

        Parameters
        ----------
        name : str
            Name of the plot
        module : Module
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
        plot: Plot = Plot(name=name, module=module, variable_name=variable_name)
        self._plots.setdefault(name, [])
        self._plots[name].append(plot)

    def plot(self, show_title: bool = True) -> None:
        """Plot all the desired variables

        Parameters
        ----------
        show_title : bool = True
            Show title on each figure

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
                plot.add_plot_to_figure(
                    figure=figure, location=location, show_title=show_title
                )
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
        # Find inputs, outputs and parameters for each module
        inputs: List[Tuple[Type, str]] = [
            (module, input_variable.name)
            for module in self.modules
            for input_variable in module.inputs
        ]
        outputs: List[Tuple[Type, str]] = [
            (module, output_variable.name)
            for module in self.modules
            for output_variable in module.outputs
        ]
        # Find all output/input combinations
        output_input_combinations: List[Tuple[str, str]] = list(
            itertools.product(*[outputs, inputs])
        )
        for output_input_combination in output_input_combinations:
            output_module_variable, input_module_variable = (
                output_input_combination
            )
            output_module, output_variable = output_module_variable
            input_module, input_variable = input_module_variable
            is_same_variable: bool = output_variable == input_variable
            is_different_module: bool = output_module != input_module
            if is_same_variable and is_different_module:
                self.add_link(
                    output_module,
                    output_variable,
                    input_module,
                    input_variable,
                )
                if self.verbose is True:
                    LOGGER.info(
                        f"Link {output_module.name}.{output_variable} to {input_module.name}.{input_variable}"
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
        cls,
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
        project.add_module(module=project_data)
        """
        for module_name in project_data[PROJECT][MODULE_COLLECTION]:
            module_instance: Module = create_class_instance(
                class_name=module_name,
                class_parameters=dict(),
                output_type=ColibriObjectTypes.MODULE,
            )
            project.add_module(module=module_instance)
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

    def _set_simulation_parameters(self) -> None:
        """Set the simulation parameters for the project orchestrator

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
        if self.project_data is None:
            return None
        for (
            parameter_name,
            parameter_value,
        ) in self.project_data.simulation_parameters.items():
            setattr(self, parameter_name, parameter_value)

    def _substitute_parameter_links_values(self):
        """"""
        # TODO: Check if it is parameters or simulation variables or both (error message)
        #       It seems that this function is to be removed, because only input/output links
        #       are created, so if to_parameter.role is Roles.PARAMETERS is always False
        for link in self.links:
            to_parameter: Parameter = link.to_module.get_field(link.to_field)
            if to_parameter is None:
                raise LinkError(
                    f"Parameter {link.to_field} was not found in module {link.to_module.name}."
                )
            if to_parameter.role is Roles.PARAMETERS:
                from_field = getattr(link.from_module, link.from_field)

    def _pass_project_data_information_to_modules(self) -> None:
        """Pass project data's information to each module that needs
        information from the project data

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
        for module in self.modules:
            parameters: List[Parameter] = module.parameters
            for parameter in parameters:
                parameter_format: str = turn_format_to_string(
                    field_format=parameter.format
                )
                if parameter_format == ProjectData.__name__:
                    setattr(module, parameter.name, self.project_data)

    def _set_intrinsic_modules_parameters_value(self) -> None:
        """Set the value for each intrinsic parameter
        (defined at the module level) of each module

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
        if self.project_data is None:
            return None
        for (
            module_class_name,
            module_parameters,
        ) in self.project_data.module_parameters.items():
            module: Module = self.get_modules_by_class(
                class_name=module_class_name
            )[0]
            for (
                module_parameter_name,
                module_parameter_value,
            ) in module_parameters.items():
                setattr(module, module_parameter_name, module_parameter_value)

    def _initialize_module_output_series(self) -> None:
        """Create a variable for each output of each module to store results at
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
        for module in self.modules:
            for variable in module.outputs:
                series_name: str = f"{variable.name}{SERIES_EXTENSION_NAME}"
                setattr(module, series_name, [0] * self.time_steps)

    def _initialize_modules(self) -> None:
        """Run the initialize method of each module in the project
        re-try until all modules are initialized to solve dependencies
        between modules

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
        is_initialization_completed: bool = False
        maximum_initialization_iterations: int = 3
        initialization_iteration: int = 0
        modules_not_initialized: Set[str] = set(
            [module.name for module in self.modules]
        )
        while (not is_initialization_completed) and (
            initialization_iteration < maximum_initialization_iterations
        ):
            are_modules_initialized: bool = True
            for module in self.modules:
                if module.has_been_initialized() is True:
                    continue
                module._is_initialized = module.initialize()
                if module.has_been_initialized() is False:
                    are_modules_initialized = False
                if module.has_been_initialized() is True:
                    modules_not_initialized.remove(module.name)
            self._substitute_links_values()
            is_initialization_completed = are_modules_initialized
            initialization_iteration += 1
        if is_initialization_completed is False:
            error_message: str = (
                f"{InitializationError.description} "
                f"Modules not initialized: "
                f"{modules_not_initialized}."
            )
            raise InitializationError(error_message)

    def _run_modules(self, time_step: int, number_of_iterations: int) -> None:
        """Run the run method of each module in the project

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
        for module in self.modules:
            if self.verbose:
                LOGGER.info(f"Computing: {module.name}")
            module.run(
                time_step=time_step,
                number_of_iterations=number_of_iterations,
            )
        print("")

    def _substitute_links_values(self) -> None:
        """Pass information (modules' values) to connected modules
        by substituting the output links' value to the input links' value

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
        """Run the end_iteration method of each module in the project

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
        for module in self.modules:
            module.end_iteration(time_step=time_step)

    def _save_module_data(self, time_step: int) -> None:
        """Run the save_time_step method of each module in the project

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
        for module in self.modules:
            module.save_time_step(time_step=time_step)

    def _end_time_step(self, time_step: int) -> None:
        """Run the end_time_step method of each module in the project

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
        for module in self.modules:
            module.end_time_step(time_step=time_step)

    def _end_simulation(self) -> None:
        """Run the end_simulation method of each module in the project

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
        for module in self.modules:
            module.end_simulation()
