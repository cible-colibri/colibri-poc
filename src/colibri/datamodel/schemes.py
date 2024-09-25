""" """

from __future__ import annotations

from enum import Enum, unique
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from colibri.config.constants import (
    BOUNDARY,
    DEFAULT,
    DESCRIPTION,
    FORMAT,
    LOGGER,
    MAX,
    MIN,
    PARAMETERS,
    SEGMENT,
    SEGMENTS,
    UNIT,
)
from colibri.utils.exceptions_utils import UserInputError

if TYPE_CHECKING:
    from colibri.datamodel.dataset import DataSet


@unique
class ColibriCategories(Enum):
    ARCHETYPES = "Archetypes"
    BOUNDARY_OBJECTS = "BoundaryObject"
    ELEMENT_OBJECTS = "ElementObject"
    STRUCTURE_OBJECTS = "StructureObject"
    MODULES = "Modules"


class Scheme:
    """Class representing the scheme of COLIBRI's objects."""

    def __init__(
        self,
        category: ColibriCategories,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new Archetype instance

        Parameters
        ----------
        category : ColibriCategories
            Category of the COLIBRI's Python object to be created ("archetype" or "project_object")
        type_name : str
            Name of the COLIBRI's project objects or archetypes
        dataset : DataSet
            DataSet object which is used to create COLIBRI's dataset (set of COLIBRI objects)
        verbose: bool = True
            Print information if set to true

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
        self.category = category
        self.type_name = type_name
        self.dataset = dataset
        self.verbose = verbose
        self.data: Dict[str, Any] = dict()
        self._scheme: Dict[str, Any] = self.dataset.schemes[category.value][
            type_name
        ]

    def initialize_data(self, kwargs) -> None:
        """

        **kwargs: Optional[Dict[str, Any]]
            Parameters' value which will be used instead of default values
        :param kwargs:
        :return:
        """
        default_to_all: bool = False
        for parameter_name, value in self._scheme[PARAMETERS].items():
            if parameter_name in kwargs:
                self.check_user_input(
                    parameter_name=parameter_name,
                    parameter_value=kwargs[parameter_name],
                )
                if parameter_name == SEGMENTS:
                    for segment in kwargs[parameter_name]:
                        segment
                        boundary: Segment = Segment(
                            dataset=self,
                            verbose=self.verbose,
                        )
                else:
                    self.data[parameter_name] = kwargs[parameter_name]
            else:
                if parameter_name in self._scheme[PARAMETERS]:
                    value: str = DEFAULT
                    if (self.dataset.assist_mode is True) and (
                        not default_to_all
                    ):
                        description: str = (
                            self.describe(
                                parameter_name=parameter_name, with_name=False
                            )
                            if self.verbose is True
                            else ""
                        )
                        value = input(
                            f"\nGive a value for {parameter_name} "
                            f"(type 'default' to use a default "
                            f"value for {parameter_name} or "
                            f"'default to all' for "
                            f"all parameters):\n\n"
                            f"{description}\n"
                        )
                        if value.lower().strip("'") == "default to all":
                            default_to_all = True
                    if (value != DEFAULT) and (not default_to_all):
                        self.check_user_input(
                            parameter_name=parameter_name, parameter_value=value
                        )
                        self.data[parameter_name] = value
                        if self.verbose:
                            LOGGER.info(
                                f"\n{parameter_name.capitalize()} set to '{value}'."
                            )
                    else:
                        default_value: Any = self._scheme[PARAMETERS][
                            parameter_name
                        ][DEFAULT]
                        self.data[parameter_name] = default_value
                        if (default_value is None) and self.verbose:
                            LOGGER.info(
                                f"\nNo default value exists. {parameter_name.capitalize()} set to '{default_value}'."
                            )
                        if (default_value is not None) and self.verbose:
                            LOGGER.info(
                                f"\n{parameter_name.capitalize()} set to '{default_value}'."
                            )

    # TODO: See code to add more functionalities and improve stuff
    def check_user_input(
        self, parameter_name: str, parameter_value: Any
    ) -> None:
        """Check if a user input value is correct

        Parameters
        ----------
        parameter_name : str
            Name of the parameter
        parameter_value : Any
            Parameter value choosen by the user

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
        parameter_data: Dict[str, Any] = self._scheme[PARAMETERS][
            parameter_name
        ]
        parameter_format: str = parameter_data[FORMAT]
        parameter_max: str = parameter_data[MAX]
        parameter_min: str = parameter_data[MIN]
        if parameter_value == "None":
            parameter_value = None
        if (
            (parameter_min is not None) or (parameter_max is not None)
        ) and parameter_value is None:
            raise UserInputError(
                f"{parameter_name} cannot be None if its limits "
                f"are defined: [{parameter_min}, {parameter_max}]."
            )
        if (
            (parameter_max is not None)
            and (parameter_max != str(float("inf")))
            and (parameter_format in ["int", "float"])
            and (float(parameter_value) > parameter_max)
        ):
            raise UserInputError(
                f"{parameter_value} for {parameter_name} is above its maximum value of {parameter_max}."
            )
        if (
            (parameter_min is not None)
            and (parameter_format in ["int", "float"])
            and (float(parameter_value) < parameter_min)
        ):
            raise UserInputError(
                f"{parameter_value} for {parameter_name} is below its minimum value of {parameter_min}."
            )
        if (
            (parameter_max is not None)
            and (parameter_max != str(float("inf")))
            and (parameter_format not in ["int", "float"])
            and (any(float(x) > parameter_max for x in parameter_value))
        ):
            raise UserInputError(
                f"{parameter_value} for {parameter_name} is above its maximum value of {parameter_max}."
            )
        if (
            (parameter_min is not None)
            and (parameter_format not in ["int", "float"])
            and (any(float(x) < parameter_min for x in parameter_value))
        ):
            raise UserInputError(
                f"{parameter_value} for {parameter_name} is below its minimum value of {parameter_min}."
            )

    def describe(
        self, parameter_name: Optional[str] = None, with_name: bool = True
    ) -> str:
        if parameter_name is None:
            message: str = f"List of parameters for the {self.type_name} ({self.category.value}) object:\n"
            for parameter_name in self._scheme[PARAMETERS]:
                unit: Any = self._scheme[PARAMETERS][parameter_name][UNIT]
                unit_message: str = f" [{unit}]\n" if unit is not None else "\n"
                message += f"- {parameter_name}: {self._scheme[PARAMETERS][parameter_name][DESCRIPTION]}{unit_message}"
            return message
        if parameter_name not in self._scheme[PARAMETERS]:
            raise ValueError(
                f"{parameter_name} is not a {self.type_name} available parameter.\n"
                f"Please, use 'describe()' to access all available parameters for this object."
            )
        parameter_data: Dict[str, Any] = self._scheme[PARAMETERS][
            parameter_name
        ]
        if with_name is True:
            message: str = f"{parameter_name}:\n{parameter_data[DESCRIPTION]}\n"
        else:
            message: str = f"{parameter_data[DESCRIPTION]}\n"
        for metadata in parameter_data.keys() - [DESCRIPTION]:
            if parameter_data[metadata] is not None:
                message += f"- {metadata}: {parameter_data[metadata]}\n"
        return message


class Archetype(Scheme):
    """Class to create specific archetypes."""

    def __init__(
        self,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new Archetype instance

        Parameters
        ----------
        type_name : str
            Name of the type of archetype (must be among the authorized archetypes)
        dataset : DataSet = None
            DataSet object in which the archetype creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            category=ColibriCategories.ARCHETYPES,
            type_name=type_name,
            dataset=dataset,
            verbose=verbose,
        )


class StructureObject(Scheme):
    """Class to create specific structure objects."""

    def __init__(
        self,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new StructureObject instance

        Parameters
        ----------
        type_name : str
            Name of the type of structure object (must be among the authorized structure objects)
        dataset : DataSet = None
            DataSet object in which the structure object creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            category=ColibriCategories.STRUCTURE_OBJECTS,
            type_name=type_name,
            dataset=dataset,
            verbose=verbose,
        )


class Boundary(StructureObject):
    """Class to create specific boundaries."""

    def __init__(
        self,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new Boundary instance

        Parameters
        ----------
        dataset : DataSet = None
            DataSet object in which the structure object creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            type_name=BOUNDARY.capitalize(),
            dataset=dataset,
            verbose=verbose,
        )


class Segment(StructureObject):
    """Class to create specific segments."""

    def __init__(
        self,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new Segment instance

        Parameters
        ----------
        dataset : DataSet = None
            DataSet object in which the structure object creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            type_name=SEGMENT.capitalize(),
            dataset=dataset,
            verbose=verbose,
        )


class BoundaryObject(Scheme):
    """Class to create specific boundary objects."""

    def __init__(
        self,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new BoundaryObject instance

        Parameters
        ----------
        type_name : str
            Name of the type of boundary object (must be among the authorized boundary objects)
        dataset : DataSet = None
            DataSet object in which the boundary object creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            category=ColibriCategories.BOUNDARY_OBJECTS,
            type_name=type_name,
            dataset=dataset,
            verbose=verbose,
        )


class ElementObject(Scheme):
    """Class to create specific element objects."""

    def __init__(
        self,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new ElementObject instance

        Parameters
        ----------
        type_name : str
            Name of the type of element object (must be among the authorized element objects)
        dataset : DataSet = None
            DataSet object in which the element object creation will be used
        verbose: bool = True
            Print information if set to true

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
        super().__init__(
            category=ColibriCategories.ELEMENT_OBJECTS,
            type_name=type_name,
            dataset=dataset,
            verbose=verbose,
        )


class Module(Scheme):
    """Class to create specific modules."""

    def __init__(
        self,
        type_name: str,
        dataset: DataSet,
        verbose: bool = True,
    ) -> None:
        """Initialize a new Module instance

        Parameters
        ----------
        type_name : str
            Name of the type of module (must be among the authorized modules)
        dataset : DataSet = None
            DataSet object in which the module creation will be used
        verbose: bool = True
            Print information if set to true
        **kwargs: Optional[Dict[str, Any]]
            Parameters' value which will be used instead of default values

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
        super().__init__(
            category=ColibriCategories.MODULES,
            type_name=type_name,
            dataset=dataset,
            verbose=verbose,
        )


if __name__ == "__main__":
    modules: List[str] = [
        "AcvExploitationOnly",
        "LimitedGenerator",
        "OccupantModel",
        "LayerWallLosses",
        "ThermalSpaceSimplified",
        "WeatherModel",
    ]
    dataset_example: DataSet = DataSet(modules=modules, verbose=True)
    #  dataset_example.describe()
    #  dataset_example.describe("Layer")
    #  dataset_example.describe("space")
    #  dataset_example.describe("layer", "thermal_conductivity")
    #  dataset_example.doc()
    #  dataset_example.add_archetype("Layer")
    #  dataset_example.add_archetype("layer")
    #  dataset_example.add_archetype("layer")
    #  dataset_example.add_archetype("layer")
    #  dataset_example.add_archetype("emitter")
    # dataset_example.describe()
    # dataset_example.describe(type_name="Emitter")
    # dataset_example.describe(
    #     category="BoundaryObject", type_name="Emitter", parameter_name="pn"
    # )
    #  dataset_example.add_archetype(type_name="Layer", archetype_id="layer-001")
    dataset_example.add_archetype(
        type_name="Layer",
        archetype_id="layer-001",
        # thickness=0.15,
        # thermal_conductivity=0.035,
    )
