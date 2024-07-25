# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import abc
import copy
from collections import namedtuple, defaultdict

from colibri.core.variables.field import Field
from colibri.utils.enums_utils import Roles


class MetaModel(abc.ABCMeta):

    def __call__(cls, *args, **kwargs):
        # automatically call all __init__ functions of parent classes, topmost first

        # Temporarily replace __init__ to prevent automatic call upon instancecreation
        original_init = cls.__init__
        cls.__init__ = lambda self, *args, **kwargs: None

        # Create the instance
        instance = super(MetaModel, cls).__call__(*args, **kwargs)

        # Restore the original __init__
        cls.__init__ = original_init

        # Initialize a set to track called __init__ methods
        called_init = set()

        # Call __init__ methods of all parent classes in the correct order
        for base in reversed(cls.__mro__):
            if '__init__' in base.__dict__ and base not in called_init:
                if issubclass(base, Model):
                    base.__init__(instance, *args, **kwargs)
                else:
                    base.__init__(instance)
                called_init.add(base)

        # Call the __init__ method of the class itself last
        if '__init__' in cls.__dict__ and cls not in called_init:
            cls.__init__(instance, *args, **kwargs)

        return instance

class Model(metaclass=MetaModel):

    def __init__(self, name: str):
        self.name = name
        self.project = None

        self._field_metadata = {}


    def field(self, name, default_value, role=None, unit=None, description=None, structure=[], linked_to = None, check_convergence = True):
        # Store the metadata in the global dictionary
        self._field_metadata[name] = Field(name, default_value, role, unit, description, structure=structure,
                                           linked_to = linked_to, check_convergence=check_convergence)

        # Return the actual value to be assigned to the variable
        return default_value

    def get_field(self, name, role: Roles = None):
        if name in self._field_metadata:
            if not role or (role and role == self._field_metadata[name].role):
                return self._field_metadata[name]

    def get_field_value(self, name):
        if hasattr(self, name):
            return getattr(self, name)

    def get_fields(self, role=None):
        if role:
            return [field for name, field in self._field_metadata.items() if field.role == role]
        else:
            return  [field for name, field in self._field_metadata.items()]

    def get_input_fields(self):
        return self.get_fields(Roles.INPUTS)

    def get_output_fields(self):
        return self.get_fields(Roles.OUTPUTS)

    def get_parameter_fields(self):
        return self.get_fields(Roles.PARAMETERS)

    def print_outputs(self):
        print(f"{self.name}:")
        for output in self.get_fields(Roles.OUTPUTS):
            print(f"{output.name}={getattr(self, output.name)} [{str(output.unit)}]")

    def is_linked(self, input):
        if self.project:
            for link in self.project.links:
                if link.to_model == self and link.to_variable == input:
                    return True
        return False

    def make_template(self, roles: [Roles]):
        template = {}
        structure_dict = {}
        for field in self.get_fields():
            if field.structure:
                for structure_field in field.structure:
                    if not roles or structure_field.role in roles:
                        structure_dict[structure_field.name] = structure_field.default_value
                if len(structure_dict) > 0:
                    if field.name in template:
                        template[field.name].append(structure_dict)
                    else:
                        template[field.name] = [structure_dict]
            else:
                if not roles or field.role in roles:
                    if field.name in template:
                        template[field.name].append(field.default_value)
                    else:
                        template[field.name] = field.default_value

        return template

    def input_template(self):
        return self.make_template([Roles.INPUTS])

    def parameter_template(self):
        return self.make_template([Roles.PARAMETERS])

    def output_template(self):
        return self.make_template([Roles.OUTPUTS])

    def input_parameter_template(self):
        return self.make_template([Roles.INPUTS, Roles.PARAMETERS])

    def template(self):
        return self.make_template(None)

    def load_from_json(self, json_in):
        for variable_name, variable_value in json_in.items():
            if isinstance(variable_value, list):
                object_list = self.create_structure(variable_name, variable_value)
                setattr(self, variable_name, object_list)
            else:
                setattr(self, variable_name, variable_value)

        for field in self.get_fields([Roles.OUTPUTS]):
            setattr(self, field.name, field.default_value)

    def create_structure(self, variable_name, variable_values):
        # this is mindboggingly complicated and maybe useless, if we require the user to replace
        # Field('space.Tint', 19, Roles.INPUTS, Units.DEGREE_CELSIUS),
        # by
        # Field('space', 19, Roles.INPUTS, Units.DEGREE_CELSIUS, structure=[
        #     Field('Tint', 19.0, Roles.PARAMETERS, Units.DEGREE_CELSIUS)
        # ]),
        #
        # and make it work ...

        object_list = []
        # create instance list
        cvf = {}
        for variable_value_dict in variable_values:
            subobject_fields = {}
            for k,v in variable_value_dict.items():
                field = k
                value = v
                if '.' in field:
                    field_name = field.split('.')[0]
                    subfield = '.'.join(field.split('.')[1:])

                    if '.' in subfield:
                        field_name1 = subfield.split('.')[0]
                        subfield1 = '.'.join(subfield.split('.')[1:])
                        existing_subfield = None
                        for f in subobject_fields[field_name]:
                            for k3, v3 in f.items():
                                if k3 == field_name1:
                                    existing_subfield = f
                        if field_name in subobject_fields:
                            if existing_subfield:
                                existing_subfield[field_name1][subfield1] = v
                            else:
                                subobject_fields[field_name].append({field_name1: {subfield1: v}})
                        else:
                            subobject_fields[field_name] = [{field_name1: {subfield1: v}}]
                        pass
                    else:
                        if field_name in subobject_fields:
                            subobject_fields[field_name].append({subfield : v})
                        else:
                            subobject_fields[field_name] = [{subfield : v}]
                else:
                    cvf[field] = value

            subobjects = {}
            for subobject_field in subobject_fields:
                if subobject_field[-1] == 's':
                    subobjects[subobject_field] = self.create_structure(subobject_field, subobject_fields[subobject_field])
                else:
                    subobjects[subobject_field] = self.create_structure(subobject_field,
                                                                        subobject_fields[subobject_field])[0]

            for field, value in subobject_fields.items():
                if not type(value) is dict:
                    cvf[field] = value

            for so, sov in subobjects.items():
                cvf[so] = sov

        object_class = namedtuple(variable_name, cvf)
        object_list.append(object_class(**cvf))

        return object_list


    @abc.abstractmethod
    def initialize(self) -> None:
        ...

    @abc.abstractmethod
    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        ...

    @abc.abstractmethod
    def iteration_done(self, time_step: int = 0) -> None:
        ...

    @abc.abstractmethod
    def timestep_done(self, time_step: int = 0) -> None:
        ...

    @abc.abstractmethod
    def simulation_done(self, time_step: int = 0) -> None:
        ...

    def converged(self, time_step: int = 0, n_iteration: int = 0) -> bool:
        return True

    def _expand_variables(self) -> None:
        variables = self.inputs + self.parameters
        for variable in variables:
            if variable.linked_to:
                for expandable_variable in variable.linked_to:
                    list_name                = expandable_variable.role
                    expandable_variable_name = expandable_variable.name
                    for index in range(0, int(variable)):
                        new_variable      = copy.deepcopy(expandable_variable)
                        new_variable.name = f"{expandable_variable_name}_{index + 1}"
                        list_to_append_to = getattr(self, list_name)
                        if any([variable for variable in list_to_append_to if variable.name == new_variable.name]):
                            variable_index = [index for index, variable in enumerate(list_to_append_to) if variable.name == new_variable.name][0]
                            list_to_append_to[variable_index] = new_variable
                        else:
                            list_to_append_to.append(new_variable)

    def save_time_step(self, time_step: int) -> None:
        for variable in self.get_output_fields():
                getattr(self, variable.name + "_series")[time_step] = copy.deepcopy(getattr(self, variable.name))


    # allow to create models for a list of modules (["models.emitters.electric_emitter"])
    # this list can be extended each time a new system model is authored
    # only systems from this list will be created automatically
    @staticmethod
    def model_factory(class_name, instance_name):
        import importlib
        for module_name in ["colibri.models.emitters.electric_emitter", "colibri.models.emitters.hydro_emitter"]:  #TODO: récupérer de manière automatique ? Ou à un autre endroit ?
            module = importlib.import_module(module_name)
            if not module is None and hasattr(module, class_name):
                cls = getattr(module, class_name)
                return cls(instance_name)

        return None

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
        string_representation = f"{self.__class__.__name__}(name = '{self.name}')"
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

# ========================================
# Functions
# ========================================
