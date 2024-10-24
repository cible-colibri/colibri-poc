"""
MetaFieldMixin class, which is a mixin for providing functionalities
related to fields' metadata for the `colibri` package.
"""

from __future__ import annotations

from inspect import FullArgSpec, getfullargspec
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from colibri.config.constants import (
    ARCHETYPES,
    ATTACHED_TO,
    CATEGORY,
    DEFAULT,
    DESCRIPTION,
    ELEMENT_OBJECT,
    FORMAT,
    PROJECT_DATA,
    REQUIRED,
    TYPE,
)
from colibri.core.fields import (
    Field,
    Parameter,
    SimulationVariable,
)
from colibri.utils.colibri_utils import (
    Attachment,
)
from colibri.utils.data_utils import turn_format_to_string
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Roles,
    Units, ColibriProjectPaths, ColibriObjectTypes,
)
from colibri.utils.exceptions_utils import AttachmentError

if TYPE_CHECKING:
    from colibri.interfaces import Module


class MetaFieldMixin:
    """Class providing functionalities related to fields' metadata."""

    def __init__(self) -> None:
        """Initialize a new MetaFieldMixin instance."""
        self._fields_metadata: Dict[str, Field] = dict()

    def define_parameter(
        self,
        name: str,
        default_value: Any,
        unit: Units,
        description: str,
        format: Any,
        min: Any,
        max: Any,
        attached_to: Optional[Attachment] = None,
        required: Optional[List[Parameter]] = None,
    ) -> Any:
        """Define a parameter (set all information into _fields_metadata)
        and return its default value

        Parameters
        ----------
        name : str
            Name of the parameter
        default_value : Any
            Default value of the parameter
        unit : Units
            Unit of the parameter
        description : str
            Description of the parameter
        format : Any
            Format of the parameter
        min : Any
            Min value of the parameter
        max : Any
            Max value of the parameter
        attached_to : Optional[Attachment] = None
            Specify which project object the parameter is attached to,
            if None, parameter is attached to the module
        required : Optional[List[Parameter]] = None
            List of required parameters inside the parameter

        Returns
        -------
        default_value : Any
            Default value associated to the parameter

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if turn_format_to_string(field_format=format) == PROJECT_DATA:
            attached_to = PROJECT_DATA
        if (required is not None) and (attached_to is None):
            raise AttachmentError(
                f"Required parameters are always relative to an attached object."
            )
        default_value: Any = self._define_field(
            name=name,
            default_value=default_value,
            unit=unit,
            role=Roles.PARAMETERS,
            description=description,
            format=format,
            min=min,
            max=max,
            attached_to=attached_to,
            required=required,
        )
        return default_value

    def define_input(
        self,
        name: str,
        default_value: Any,
        unit: Units,
        description: str,
        format: Any,
        min: Any,
        max: Any,
        attached_to: Attachment,
    ) -> Any:
        """Define a input (set all information into _fields_metadata)
        and return its default value

        Parameters
        ----------
        name : str
            Name of the input
        default_value : Any
            Default value of the input
        unit : Units
            Unit of the input
        description : str
            Description of the input
        format : Any
            Format of the input
        min : Any
            Min value of the input
        max : Any
            Max value of the input
        attached_to : Attachment
            Specify which project object the input is attached to

        Returns
        -------
        default_value : Any
            Default value associated to the input

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        default_value: Any = self._define_field(
            name=name,
            default_value=default_value,
            unit=unit,
            role=Roles.INPUTS,
            description=description,
            format=format,
            min=min,
            max=max,
            attached_to=attached_to,
        )
        return default_value

    def define_output(
        self,
        name: str,
        default_value: Any,
        unit: Units,
        description: str,
        format: Any,
        min: Any,
        max: Any,
        attached_to: Attachment,
    ) -> Any:
        """Define a output (set all information into _fields_metadata)
        and return its default value

        Parameters
        ----------
        name : str
            Name of the output
        default_value : Any
            Default value of the output
        unit : Units
            Unit of the output
        description : str
            Description of the output
        format : Any
            Format of the output
        min : Any
            Min value of the output
        max : Any
            Max value of the output
        attached_to : Attachment
            Specify which project object the output is attached to

        Returns
        -------
        default_value : Any
            Default value associated to the output

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        default_value: Any = self._define_field(
            name=name,
            default_value=default_value,
            unit=unit,
            role=Roles.OUTPUTS,
            description=description,
            format=format,
            min=min,
            max=max,
            attached_to=attached_to,
        )
        return default_value

    def _define_field(
        self,
        name: str,
        default_value: Any,
        role: Roles,
        unit: Units,
        description: str,
        format: Any,
        min: Any,
        max: Any,
        attached_to: Optional[Attachment] = None,
        required: Optional[List[Parameter]] = None,
    ) -> Any:
        """Define the field (set all information into _fields_metadata)
        and return its default value

        Parameters
        ----------
        name : str
            Name of the field
        default_value : Any
            Default value of the field
        role : Roles
            Role of the field
        unit : Units
            Unit of the field
        description : str
            Description of the field
        format : Any
            Format of the field's value
        min : Optional[Any] = None
            Min value of the field
        max : Optional[Any] = None
            Max value of the field
        attached_to : Optional[Attachment] = None
            Project object from which the field is attached to
        required : Optional[List[Parameter]] = None
            List of required parameters inside the parameter

        Returns
        -------
        default_value : Any
            Default value associated to the field

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        linked_to: List[Field] = list()
        model: Optional[Module] = None
        check_convergence: bool = False
        convergence_tolerance: float = 0.1
        maximum_number_of_iterations: int = 10
        if role is Roles.PARAMETERS:
            self._fields_metadata[name] = Parameter(
                name=name,
                default_value=default_value,
                role=role,
                unit=unit,
                description=description,
                format=format,
                min=min,
                max=max,
                attached_to=attached_to,
                required=required,
            )
            return default_value
        self._fields_metadata[name] = SimulationVariable(
            name=name,
            default_value=default_value,
            role=role,
            unit=unit,
            description=description,
            format=format,
            min=min,
            max=max,
            linked_to=linked_to,
            model=model,
            check_convergence=check_convergence,
            convergence_tolerance=convergence_tolerance,
            maximum_number_of_iterations=maximum_number_of_iterations,
            attached_to=attached_to,
            required=required,
        )
        return default_value

    @property
    def inputs(self) -> List[Field]:
        """Get all field inputs of the model

        Returns
        -------
        inputs : List[Field]
            All field inputs of the model

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        inputs: List[Field] = self.get_fields(role=Roles.INPUTS)
        return inputs

    @property
    def outputs(self) -> List[Field]:
        """Get all field outputs of the model

        Returns
        -------
        outputs : List[Field]
            All field outputs of the model

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        outputs: List[Field] = self.get_fields(role=Roles.OUTPUTS)
        return outputs

    @property
    def parameters(self) -> List[Field]:
        """Get all field parameters of the model

        Returns
        -------
        parameters : List[Field]
            All field parameters of the model

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        parameters: List[Field] = self.get_fields(role=Roles.PARAMETERS)
        return parameters

    def get_fields(self, role: Optional[Roles] = None) -> List[Field]:
        """Get the fields of the model (for a given role if provided)

        Parameters
        ----------
        role : Optional[Roles] = None
            Role of the field

        Returns
        -------
        List[Field]
            Fields of the model (for a given role if provided)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if role:
            return [
                field
                for field in self._fields_metadata.values()
                if field.role == role
            ]
        return [field for field in self._fields_metadata.values()]

    @classmethod
    def to_scheme(cls) -> Dict[str, Any]:
        """Get the field's scheme

        Returns
        -------
        Dict[str, Any]
            Scheme of the field

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        model_metadata: FullArgSpec = getfullargspec(cls.__init__)
        required_parameters: List[str] = model_metadata.args[1:]
        instance: MetaFieldMixin = cls(
            **{name: None for name in required_parameters}
        )
        module_parameters: Dict[str, Any] = {
            module_parameter.name: module_parameter.to_scheme()
            for module_parameter in instance.parameters
        }
        module_inputs: Dict[str, Any] = {
            module_input.name: module_input.to_scheme()
            for module_input in instance.inputs
        }
        scheme: Dict[str, Any] = dict()
        for input_name, input_data in module_inputs.items():
            _ = input_data.pop(REQUIRED)
            attachment: Attachment = input_data.pop(ATTACHED_TO)
            cls._build_scheme(
                scheme=scheme,
                field_name=input_name,
                field_data=input_data,
                attachment=attachment,
                instance=instance,
            )
        for parameter_name, parameter_data in module_parameters.items():
            attachment: Attachment = parameter_data.pop(ATTACHED_TO)
            required_parameters: List[Parameter] = parameter_data.pop(REQUIRED)
            # Parameters can be defined at the module level or
            # at the ProjectData level
            if (
                turn_format_to_string(field_format=parameter_data[FORMAT])
                == PROJECT_DATA
            ):
                for required_parameter in required_parameters:
                    field_name: str = required_parameter.name
                    field_data: Dict[str, Any] = required_parameter.to_scheme()
                    attachment: Attachment = field_data.pop(ATTACHED_TO)
                    cls._build_scheme(
                        scheme=scheme,
                        field_name=field_name,
                        field_data=field_data,
                        attachment=attachment,
                        instance=instance,
                    )
            else:
                cls._build_scheme(
                    scheme=scheme,
                    field_name=parameter_name,
                    field_data=parameter_data,
                    attachment=attachment,
                    instance=instance,
                )
        return scheme

    @staticmethod
    def _build_scheme(
        scheme: Dict[str, Any],
        field_name: str,
        field_data: Dict[str, Any],
        attachment: Attachment,
        instance: MetaFieldMixin,
    ):
        class_name = instance.__class__.__name__
        category: ColibriProjectObjects = (
            attachment.category if attachment is not None else None
        )
        if category is None:
            scheme.setdefault(class_name, dict())
            scheme[class_name][field_name] = field_data
            if hasattr(instance, TYPE.upper()):
                scheme[class_name].update({TYPE: instance.TYPE})
            if hasattr(instance, DESCRIPTION.upper()):
                scheme[class_name].update({DESCRIPTION: instance.DESCRIPTION})
        else:
            category: ColibriProjectObjects = attachment.category
            class_name: str = attachment.class_name
            from_archetype: bool = attachment.from_archetype
            from_element_object: str = attachment.from_element_object
            description: str = attachment.description
            format: Any = attachment.format
            default_value: Any = attachment.default_value
            # Update field's description and format with those from the attachment,
            # in case the inputs is a kind of aggregation of the attachment
            if description is not None:
                field_data.update({DESCRIPTION: description})
            if format is not None:
                field_data.update({FORMAT: format})
            if default_value is not None:
                field_data.update({DEFAULT: default_value})
            # Regular field
            if ( #why?
                category
                not in [
                    ColibriProjectObjects.BOUNDARY_OBJECT,
                    ColibriProjectObjects.ELEMENT_OBJECT,
                ]
            ) and (from_element_object is None):
                scheme.setdefault(category.value, dict())
                scheme[category.value][field_name] = field_data
            # Field from a boundary object
            if (
                (
                    category
                    in [
                        ColibriProjectObjects.BOUNDARY_OBJECT,
                        ColibriProjectObjects.ELEMENT_OBJECT,
                    ]
                )
                and (from_archetype is True)
                and (from_element_object is None)
            ):
                scheme.setdefault(ARCHETYPES.capitalize(), dict())
                scheme[ARCHETYPES.capitalize()].setdefault(
                    class_name, {CATEGORY: category.value}
                )
                scheme[ARCHETYPES.capitalize()][class_name][field_name] = (
                    field_data
                )
            if (
                (
                    category
                    in [
                        ColibriProjectObjects.BOUNDARY_OBJECT,
                        ColibriProjectObjects.ELEMENT_OBJECT,
                    ]
                )
                and (from_archetype is False)
                and (from_element_object is None)
            ):
                scheme.setdefault(class_name, {CATEGORY: category.value})
                scheme[class_name][field_name] = field_data
            # Field from an element object
            if (
                category
                not in [
                    ColibriProjectObjects.BOUNDARY_OBJECT,
                    ColibriProjectObjects.ELEMENT_OBJECT,
                ]
            ) and (from_element_object is not None):
                scheme.setdefault(ELEMENT_OBJECT, dict())
                scheme[ELEMENT_OBJECT].setdefault(
                    from_element_object,
                    {CATEGORY: category.value, ATTACHED_TO: class_name},
                )
                scheme[ELEMENT_OBJECT][from_element_object][field_name] = (
                    field_data
                )

    @classmethod
    def to_template(cls) -> Dict[str, Any]:
        from colibri.utils.class_utils import get_class

        scheme = cls.to_scheme()

        project_dict = {}

        for scheme_object, variables in scheme.items():
            path = ColibriProjectPaths.get_path_from_object_type(scheme_object)
            if not path and 'category' in variables:
                path = ColibriProjectPaths.get_path_from_object_type(variables['category'])
                variables.pop('category', None)
            if path:
                level = project_dict
                for attribute in path.split('.'):
                    if attribute not in level:
                        if attribute == 'object_collection':
                            level[attribute] = []
                        else:
                            level[attribute] = {}
                    level = level[attribute]

                object_name = scheme_object
                id = scheme_object + "1"

                object_dict = {}
                if object_name not in level:
                    object_dict['type'] = object_name
                    model_class = get_class(
                        class_name=object_name,
                        output_type=ColibriObjectTypes.PROJECT_OBJECT,
                    )
                    model_metadata: FullArgSpec = getfullargspec(model_class.__init__)
                    required_parameters: List[str] = model_metadata.args[1:]
                    for parameter in required_parameters:
                        object_dict[parameter] = None

                for name, variable in variables.items():
                    if 'default' in variable:
                        object_dict[name] = variable['default']

                if isinstance(level, list):
                    level.append(object_dict)
                else:
                    level[id] = object_dict
        archetypes = scheme['Archetypes']
        archetypes_instance = {}

        for k,v in archetypes.items():
            name = k + "1"
            archetypes_instance[k] = { name: v}

        project_dict['project']['archetype_collection'] = archetypes

        return project_dict

    # TODO: Any -> Module instance
    @classmethod
    def from_template(cls, template: Dict[str, Any]) -> object:
        """Create a module instance ready to be used from a template
        specific to the module

        Parameters
        ----------
        template: Dict[str, Any]
            Specific template for the module

        Returns
        -------
        object
            Module instance

        Raises
        ------
        None

        Examples
        --------
        >>> limited_generator = LimitedGenerator.from_template(template=template)
        >>> limited_generator.initialize()
        >>> limited_generator.run(time_step=1, number_of_iterations=1)
        >>> limited_generator.end_time_step(time_step=1)
        >>> limited_generator.end_iteration(time_step=1)
        >>> limited_generator.end_simulation()
        >>> limited_generator.q_consumed
        """
        from colibri.core import ProjectData
        name: str = f"{ProjectData.INSTANCE_NAME}_1"
        project_data: ProjectData = ProjectData(name=name, data=template)
        model_metadata: FullArgSpec = getfullargspec(cls.__init__)
        required_parameters: List[str] = model_metadata.args[1:]
        parameters: Dict[str, Any] = {"name": f"{cls.__name__.lower()}-1"}
        module_collection: Dict[str, Dict[str, Any]] = template["project"]["module_collection"]
        # Module needs some specific parameters
        if cls.__name__ in module_collection:
            parameters.update(module_collection[cls.__name__])
        # Module needs ProjectData instance "project_data"
        if ProjectData.INSTANCE_NAME in required_parameters:
            parameters.update({ProjectData.INSTANCE_NAME: project_data})
        return cls(**parameters)
