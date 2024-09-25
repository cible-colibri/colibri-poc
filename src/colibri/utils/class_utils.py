"""
Helper classes or functions when working with classes for the `colibri` package.
"""

import importlib
import inspect
from inspect import FullArgSpec
from types import ModuleType
from typing import Any, Dict, List, Tuple, Type, Union

from colibri.config.constants import (
    COLIBRI_INTERFACES_MODULE_PATH,
    COLIBRI_MODULES_MODULE_PATH,
    COLIBRI_PROJECT_OBJECTS_MODULE_PATH,
)
from colibri.interfaces import ElementObject
from colibri.utils.enums_utils import ColibriObjectTypes
from colibri.utils.exceptions_utils import (
    ColibriModuleNotFoundError,
    UnauthorizedColibriModule,
)


def get_class(class_name: str, output_type: ColibriObjectTypes) -> Type:
    """Return a class given its name

    Parameters
    ----------
    class_name : str
        Name of the class to be returned
    output_type : ColibriObjectTypes
        Type of output expected

    Returns
    -------
    class_signature : Type
        Class signature

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    classes_path: str = (
        COLIBRI_MODULES_MODULE_PATH
        if output_type is ColibriObjectTypes.MODEL
        else COLIBRI_PROJECT_OBJECTS_MODULE_PATH
    )
    colibri_classes_module: ModuleType = importlib.import_module(classes_path)
    if hasattr(colibri_classes_module, class_name) is False:
        class_signature: Type = ElementObject
        return class_signature
    class_signature: Type = getattr(colibri_classes_module, class_name)
    return class_signature


def create_class_instance(
    class_name: str,
    class_parameters: Dict[str, Any],
    output_type: ColibriObjectTypes,
) -> Union["BoundaryObject", "Model", "StructureObject"]:
    """Create an instance of a class given its name

    Parameters
    ----------
    class_name : str
        Name of the class to be instanciated
    class_parameters : Dict[str, Any]
        Parameters required to create the instance of the class
    output_type : ColibriObjectTypes
        Type of output expected

    Returns
    -------
    instance : Union[BoundaryObject, Model, StructureObject]
        Instance of the class

    Raises
    ------
    ColibriModuleNotFoundError
        If the module does not exist
    UnauthorizedColibriModule
        If the module is unauthorized

    Examples
    --------
    >>> None
    """
    # Define the paths where to find the classes and interfaces
    classes_path: str = COLIBRI_MODULES_MODULE_PATH
    interfaces_path: Union[str, None] = COLIBRI_INTERFACES_MODULE_PATH
    # Classes and interfaces are different for project objects
    if output_type is ColibriObjectTypes.PROJECT_OBJECT:
        classes_path = COLIBRI_PROJECT_OBJECTS_MODULE_PATH
        interfaces_path = None
    # Check that the class exists
    colibri_classes_module: ModuleType = importlib.import_module(classes_path)
    if hasattr(colibri_classes_module, class_name) is False:
        raise ColibriModuleNotFoundError(f"{class_name} is not a valid model.")
    model_class: Type = getattr(colibri_classes_module, class_name)
    # Check that the interface is acceptable
    if interfaces_path is not None:
        colibri_interfaces_module: ModuleType = importlib.import_module(
            COLIBRI_INTERFACES_MODULE_PATH
        )
        colibri_interfaces: List[str] = dir(colibri_interfaces_module)
        parent_model_class_name: Type = model_class.__bases__[0].__name__
        if parent_model_class_name not in colibri_interfaces:
            raise UnauthorizedColibriModule(
                f"{class_name} of {model_class} class is not a subclass "
                f"of the available scheme configuration."
            )
    model_metadata: FullArgSpec = inspect.getfullargspec(model_class.__init__)
    required_parameters: List[str] = model_metadata.args[1:]
    temporary_default_parameters_values: Tuple[Any] | None = (
        model_metadata.defaults
    )
    default_parameters_values: Dict[str, Any] = dict()
    if temporary_default_parameters_values is not None:
        reversed_parameters: List[str] = required_parameters[::-1]
        reversed_default_parameters_values: Tuple[Any] = (
            temporary_default_parameters_values[::-1]
        )
        missing_default_values: int = len(reversed_parameters) - len(
            reversed_default_parameters_values
        )
        default_parameters_values: Dict[str, Any] = dict(
            zip(
                reversed_parameters,
                reversed_default_parameters_values
                + (None,) * missing_default_values,
            )
        )
    parameters: Dict[str, Any] = {
        name: class_parameters.get(
            name, default_parameters_values.get(name, None)
        )
        for name in required_parameters
    }
    instance: object = model_class(**parameters)
    if output_type is ColibriObjectTypes.PROJECT_OBJECT:
        for name, value in class_parameters.items():
            if name not in parameters:
                setattr(instance, name, value)
    return instance


if __name__ == "__main__":
    from colibri.config.constants import LOGGER
    from colibri.utils.enums_utils import ColibriObjectTypes

    class_signature = get_class(
        class_name="AcvExploitationOnly",
        output_type=ColibriObjectTypes.MODEL,
    )
    LOGGER.debug(class_signature)
    class_signature = get_class(
        class_name="Space",
        output_type=ColibriObjectTypes.PROJECT_OBJECT,
    )
    LOGGER.debug(class_signature)
    class_signature = get_class(
        class_name="Layer",
        output_type=ColibriObjectTypes.PROJECT_OBJECT,
    )
    LOGGER.debug(class_signature)
    acv = create_class_instance(
        class_name="AcvExploitationOnly",
        class_parameters={"name": "model-1"},
        output_type=ColibriObjectTypes.MODEL,
    )
    LOGGER.debug(acv)
    space = create_class_instance(
        class_name="Space",
        class_parameters={
            "id": "living_room_1",
            "label": "salon",
        },
        output_type=ColibriObjectTypes.PROJECT_OBJECT,
    )
    LOGGER.debug(space)
    space = create_class_instance(
        class_name="Space",
        class_parameters={
            "id": "living_room_1",
            "label": "salon",
            "volume": 52.25,
            "use": "living room",
        },
        output_type=ColibriObjectTypes.PROJECT_OBJECT,
    )
    LOGGER.debug(space)
