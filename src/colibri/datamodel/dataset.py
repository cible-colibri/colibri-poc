"""DataSet class to create data sets for COLIBRI."""

import ast
import copy
import math
import uuid
from enum import Enum, unique
from typing import Any, Dict, List, Optional, Tuple, Type

from colibri.config.constants import (
    ARCHETYPES,
    BOUNDARY,
    DESCRIPTION,
    LOGGER,
    TYPE,
)
from colibri.core import ProjectOrchestrator
from colibri.datamodel.schemes import (
    Archetype,
    Boundary,
    BoundaryObject,
    ElementObject,
    Module,
    StructureObject,
)
from colibri.mixins.class_mixin import ClassMixin
from colibri.project_objects import Segment
from colibri.utils.data_utils import are_dictionaries_equal
from colibri.utils.exceptions_utils import UserInputError


@unique
class ColibriCategories(Enum):
    ARCHETYPES = "Archetypes"
    BOUNDARY_OBJECTS = "BoundaryObject"
    ELEMENT_OBJECTS = "ElementObject"
    STRUCTURE_OBJECTS = "StructureObject"
    MODULES = "Modules"


class DataSet(ClassMixin):
    """Class representing a data set, which can be built with the class's functions."""

    def __init__(
        self,
        modules: List[str],
        data: Optional[Dict[str, Any]] = None,
        assist_mode: bool = True,
        verbose: bool = False,
    ) -> None:
        """Initialize a new DataSet instance."""

        self.modules = modules
        self.schemes: Dict[str, Any] = ProjectOrchestrator.generate_scheme(
            modules=modules
        )
        self.assist_mode = assist_mode
        self.verbose = verbose

        self.archetype_names: List[str] = [
            archetype_name
            for archetype_name in self.schemes[ARCHETYPES.capitalize()]
        ]
        self.boundary_object_names: List[str] = [
            boundary_object_name
            for boundary_object_name in self.schemes["BoundaryObject"]
        ]
        self.module_names: List[str] = [
            module_name for module_name in self.schemes["Modules"]
        ]
        self.structure_object_names: List[str] = [
            structure_object_name
            for structure_object_name in self.schemes["StructureObject"]
        ]

        if data is None:
            self.building_land: Dict[str, Any] = dict()
            self.structure_object_collection: Dict[str, Any] = dict()
            self.boundary_collection: Dict[str, Any] = dict()
            self.archetype_collection: Dict[str, Any] = dict()
            self.unique_ids: List[str] = []
            # By default, DataSet is set for 3D representation of buildings.
            # If 3D info are not given, it will be set as False (1D model)
            self.three_dimensional_model: bool = True

    def generate_unique_id(self, prefix: str) -> str:
        """Generate a unique dataset identifier (ID) constructed on the following model {prefix}_{random_number}

        Parameters
        ----------
        prefix : str
            Prefix used to create the identifier (ID)

        Returns
        -------
        identifier : str
            Unique identifier (ID)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        random_id: str = str(uuid.uuid4())
        identifier: str = f"{prefix}_{random_id}"
        self.unique_ids.append(identifier)
        return identifier

    def add_archetype(
        self,
        type_name: str,
        archetype_id: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> str:
        """Add an archetype to the dataset's archetype_collection

        Parameters
        ----------
        type_name : str
            Name of the type of archetype (must be among the authorized archetypes)
        archetype_id : Optional[str] = None
            Unique identifier (ID) of the archetype
        **kwargs: Optional[Dict[str, Any]]
            Parameters' value which will be used instead of default values

        Returns
        -------
        archetype_id : str
            Unique identifier (ID) of the archetype

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if type_name not in self.archetype_names:
            raise ValueError(
                f"{type_name} is not a available archetype. "
                f"Please, choose among : {self.archetype_names}."
            )
        if archetype_id is None:
            archetype_id: str = input(
                "\nSet your own archetype_id (must be a unique string) "
                "or type 'no' to generate one randomly: "
            )
            if (not archetype_id) or (archetype_id.lower().strip("'") == "no"):
                archetype_id: str = self.generate_unique_id(prefix=type_name)
                if self.verbose:
                    LOGGER.info(f"\nArchetype id set to '{archetype_id}'")
            elif archetype_id in self.unique_ids:
                old_archetype_id: str = archetype_id
                archetype_id: str = self.generate_unique_id(prefix=type_name)
                if self.verbose:
                    LOGGER.info(
                        f"\nGiven id '{old_archetype_id}' was already used, so "
                        f"the archetype id has been set to '{archetype_id}'"
                    )
        self.unique_ids.append(archetype_id)
        if kwargs is None:
            kwargs = dict()
        label: str = kwargs.get("label", None)
        if label is None:
            label: str = input(
                "\nMissing archetype label. "
                "Set your own archetype label (string).\n"
                "Labels are not used for computation, "
                "but could be displayed in graphical user interfaces.\n"
                "Type 'no' to use the id as a label: "
            )
            if (not label) or (label.lower().strip("'") == "no"):
                label = archetype_id
            kwargs["label"] = label
            if self.verbose:
                LOGGER.info(f"\nLabel set to '{label}'")
        archetype: Archetype = Archetype(
            type_name=type_name,
            dataset=self,
            verbose=self.verbose,
        )
        archetype.initialize_data(kwargs)
        # Test if an archetype with the same characteristics already exists.
        # If so, ask if a second one should be created
        does_archetype_already_exist: bool = False
        if f"{type_name}_types" in self.archetype_names:
            for archetype_key, archetype_item in self.archetype_collection[
                f"{type_name}_types"
            ].items():
                are_archetypes_the_same: bool = are_dictionaries_equal(
                    dict_1=archetype_item,
                    dict_2=archetype.data,
                    keys_to_be_excluded=["label"],
                )
                if are_archetypes_the_same:
                    does_archetype_already_exist = True
                    same_archetype_id = archetype_key
                    same_archetype_label = archetype_item["label"]
                    break
        if does_archetype_already_exist:
            choice: str = input(
                f"A identical archetype already exists with the same "
                f"properties: ('id': '{same_archetype_id}',"
                f"'label': '{same_archetype_label}').\n"
                f"Type 'yes' if you want to use it or 'no' to keep creating a new one with id {archetype_id} and label {label}: "
            )
            if choice.lower().strip("'") == "yes":
                return same_archetype_id
        if f"{type_name}_types" not in self.archetype_collection:
            self.archetype_collection[f"{type_name}_types"] = dict()
        self.archetype_collection[f"{type_name}_types"][archetype_id] = (
            archetype.data
        )
        if self.verbose:
            rapport = (
                f"{type_name.capitalize()} archetype added successfully to dataset"
                f" with id '{archetype_id}' and the following data:\n"
                f"{archetype.data}\n"
            )
            LOGGER.info(rapport)
        return archetype_id

    def add_structure_object(
        self,
        type_name: str,
        structure_object_id: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> str:
        """Add a structure object to the dataset's structure_object_collection

        Parameters
        ----------
        type_name : str
            Name of the type of structure object (must be among the authorized structure objects)
        structure_object_id : Optional[str] = None
            Unique identifier (ID) of the structure object
        **kwargs: Optional[Dict[str, Any]]
            Parameters' value which will be used instead of default values

        Returns
        -------
        structure_object_id : str
            Unique identifier (ID) of the structure object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if type_name not in self.structure_object_names:
            raise ValueError(
                f"{type_name} is not a available structure object. "
                f"Please, choose among : {self.structure_object_names}."
            )
        if structure_object_id is None:
            structure_object_id: str = input(
                "\nSet your own structure_object_id (must be a unique string) "
                "or type 'no' to generate one randomly: "
            )
            if (not structure_object_id) or (
                structure_object_id.lower().strip("'") == "no"
            ):
                structure_object_id: str = self.generate_unique_id(
                    prefix=type_name
                )
                if self.verbose:
                    LOGGER.info(
                        f"\nStructure object id set to '{structure_object_id}'"
                    )
            elif structure_object_id in self.unique_ids:
                old_structure_object_id: str = structure_object_id
                structure_object_id: str = self.generate_unique_id(
                    prefix=type_name
                )
                if self.verbose:
                    LOGGER.info(
                        f"\nGiven id '{old_structure_object_id}' was already used, so "
                        f"the structure object id has been set to '{structure_object_id}'"
                    )
        self.unique_ids.append(structure_object_id)
        if kwargs is None:
            kwargs = dict()
        kwargs.update({"id": structure_object_id})
        label: str = kwargs.get("label", None)
        if label is None:
            label: str = input(
                "\nMissing structure object label. "
                "Set your own structure object label (string).\n"
                "Labels are not used for computation, "
                "but could be displayed in graphical user interfaces.\n"
                "Type 'no' to use the id as a label: "
            )
            if (not label) or (label.lower().strip("'") == "no"):
                label = structure_object_id
            kwargs["label"] = label
            if self.verbose:
                LOGGER.info(f"\nLabel set to '{label}'")
        structure_object: StructureObject = StructureObject(
            type_name=type_name,
            dataset=self,
            verbose=self.verbose,
        )
        structure_object.initialize_data(kwargs)
        if f"{type_name}_collection" not in self.structure_object_collection:
            self.structure_object_collection[f"{type_name}_collection"] = dict()
        self.structure_object_collection[f"{type_name}_collection"][
            structure_object_id
        ] = structure_object.data
        if self.verbose:
            rapport = (
                f"{type_name.capitalize()} node added successfully to dataset"
                f" with id '{structure_object_id}' and the following data:\n"
                f"{structure_object.data}\n"
            )
            LOGGER.info(rapport)
        return structure_object_id

    def add_boundary(
        self,
        boundary_id: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> str:
        """Add a boundary to the dataset's boundary_collection

        Parameters
        ----------
        boundary_id : Optional[str] = None
            Unique identifier (ID) of the boundary
        **kwargs: Optional[Dict[str, Any]]
            Parameters' value which will be used instead of default values

        Returns
        -------
        boundary_id : str
            Unique identifier (ID) of the boundary

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if boundary_id is None:
            boundary_id: str = input(
                "\nSet your own boundary_id (must be a unique string) "
                "or type 'no' to generate one randomly: "
            )
            if (not boundary_id) or (boundary_id.lower().strip("'") == "no"):
                boundary_id: str = self.generate_unique_id(prefix=BOUNDARY)
                if self.verbose:
                    LOGGER.info(f"\nBoundary id set to '{boundary_id}'")
            elif boundary_id in self.unique_ids:
                old_boundary_id: str = boundary_id
                boundary_id: str = self.generate_unique_id(prefix=BOUNDARY)
                if self.verbose:
                    LOGGER.info(
                        f"\nGiven id '{old_boundary_id}' was already used, so "
                        f"the boundary id has been set to '{boundary_id}'"
                    )
        self.unique_ids.append(boundary_id)
        if kwargs is None:
            kwargs = dict()
        kwargs.update({"id": boundary_id})
        label: str = kwargs.get("label", None)
        if label is None:
            label: str = input(
                "\nMissing boundary label. "
                "Set your own boundary label (string).\n"
                "Labels are not used for computation, "
                "but could be displayed in graphical user interfaces.\n"
                "Type 'no' to use the id as a label: "
            )
            if (not label) or (label.lower().strip("'") == "no"):
                label = boundary_id
            kwargs["label"] = label
            if self.verbose:
                LOGGER.info(f"\nLabel set to '{label}'")
        boundary: Boundary = Boundary(
            dataset=self,
            verbose=self.verbose,
        )
        boundary.initialize_data(kwargs)
        if f"{BOUNDARY}_collection" not in self.boundary_collection:
            self.boundary_collection[f"{BOUNDARY}_collection"] = dict()
        self.boundary_collection[f"{BOUNDARY}_collection"][boundary_id] = (
            boundary.data
        )
        if self.verbose:
            rapport = (
                f"{BOUNDARY.capitalize()} node added successfully to dataset"
                f" with id '{boundary_id}' and the following data:\n"
                f"{boundary.data}\n"
            )
            LOGGER.info(rapport)
        return boundary_id

    def warn_and_set_to_1d_model(self) -> None:
        """Warn that datamodel is set to 1D model only (self.three_dimensional_model = False)

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
        LOGGER.warning(
            "Don't use 2D/3D representation for boundaries by settings 'segment' parameter."
            "\nTherefore your data set model will set as 1D model only\n"
            "(no 3D representation, no known adjacency between boundary."
        )
        self.three_dimensional_model = False

    def describe(
        self,
        category: Optional[str] = None,
        type_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
    ) -> None:
        """Provide/print help/documentation about dataset objects' parameters

        Parameters
        ----------
        category : Optional[str]
            Category of the object (in which scheme to search for).
            If not set, use the first one. Possible values are:
                - "Archetypes"
                - "BoundaryObject"
                - "ElementObject"
                - "StructureObject"
                - "Modules"
        type_name : Optional[str]
            Name of the type of object (among a given category)
        parameter_name : Optional[str]
            Name of the parameter of a given object (category and type_name)

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
        message: str = ""
        if (type_name is not None) and (category is not None):
            category_object_mapper: Dict[str, Type] = {
                ColibriCategories.ARCHETYPES.value: Archetype,
                ColibriCategories.BOUNDARY_OBJECTS.value: BoundaryObject,
                ColibriCategories.ELEMENT_OBJECTS.value: ElementObject,
                ColibriCategories.STRUCTURE_OBJECTS.value: StructureObject,
                ColibriCategories.MODULES.value: Module,
            }
            message += category_object_mapper[category](
                type_name=type_name, dataset=self, verbose=False
            ).describe(parameter_name=parameter_name)
        if (type_name is not None) and (category is None):
            if type_name in self.archetype_names:
                message += Archetype(
                    type_name=type_name, dataset=self, verbose=False
                ).describe(parameter_name=parameter_name)
            if type_name in self.boundary_object_names:
                message += BoundaryObject(
                    type_name=type_name, dataset=self, verbose=False
                ).describe(parameter_name=parameter_name)
            if type_name in self.module_names:
                message += Module(
                    type_name=type_name, dataset=self, verbose=False
                ).describe(parameter_name=parameter_name)
            if type_name in self.structure_object_names:
                message += StructureObject(
                    type_name=type_name, dataset=self, verbose=False
                ).describe(parameter_name=parameter_name)
        if type_name is None:
            message += (
                "COLIBRI dataset is composed of archetypes, modules, or "
                "project objects (structure, boundary or element objects).\n"
                "COLIBRI structure objects are:\n\n"
            )
            for structure_object in self.structure_object_names:
                message += (
                    f"{self.schemes['StructureObject'][structure_object][TYPE]}:"
                    f" {self.schemes['StructureObject'][structure_object][DESCRIPTION]}\n\n"
                )
            message += "COLIBRI boundary objects are:\n\n"
            for boundary_object in self.boundary_object_names:
                message += (
                    f"{boundary_object}:"
                    f" {self.schemes['BoundaryObject'][boundary_object][DESCRIPTION]}\n\n"
                )
            message += "COLIBRI archetypes are:\n\n"
            for archetype_object in self.archetype_names:
                message += (
                    f"{archetype_object}:"
                    f" {self.schemes['Archetypes'][archetype_object][DESCRIPTION]}\n\n"
                )
            message += "COLIBRI modules (with parameters) are:\n\n"
            for module in self.module_names:
                message += (
                    f"{module}:"
                    f" {self.schemes['Modules'][module][DESCRIPTION]}\n\n"
                )
            message += (
                "To learn more about each object's parameters, use: "
                "describe(type_name=<type_name>)\n"
                "To learn more about a specific parameter of a given object, use: "
                "describe(type_name=<type_name>, parameter_name=<parameter_name>)\n"
                "To learn more about how you can create the COLIBRI's dataset, use: "
                "doc()"
            )
        LOGGER.info(message)

    def create_segment_and_compute_area_from_coordinates(
        self,
        ordered_coordinates: Optional[List[Tuple[float, float]]] = None,
        ordered_names: Optional[List[str]] = None,
    ) -> Tuple[List[Segment], float]:
        """Create segments and compute area from given or ask coordinates

        Parameters
        ----------
        ordered_coordinates: Optional[List[Tuple[float, float]]] = None
            List of x,y coordinates [[x,y],[x1,y1...] in lambert93 (meters)
            used to describe the shape of a boundary in a plane reference
            coordinnates systems [0,0] is always one of the point of the
            boundary shape (the bottom left).
            Important: coordinates needs to be set in CLOCKWISE order.
        ordered_names: Optional[List[str]] = None
            List of names

        Returns
        -------
        Tuple[List[Segment], float]
            segments : List[Segment]
                List of segments (without junction yet) in COLIBRI boundary segment format
            area : float
                Surface area from given coordinates (shape points)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if ordered_coordinates is None:
            user_input = "start"
            ordered_coordinates = [[0, 0]]
            print(
                "\nPlease enter each coordinates in the format [x, y] to describe the shape of the boundary in its 2D reference frame."
                "\nPLEASE RESPECT THE CLOCKWISE ORDER OF THE POINT BY FOLLOWING SEGMENT BETWEEN EACH POINT.\nTYPE '' OR 'end' when finished."
                "\nThe first point always starts with [0, 0] and has already been provided (no need to set it again)."
                "\nPlace the other points relative to this one, ideally considering it as the bottom-left point of your shape (in order to have positive x and y values ideally)"
            )
            i = 2
            print("Point number 1 : [0,0] saved \n")
            while user_input not in ["end", ""]:
                user_input = input(
                    f"Please enter point number {i} in the format [x, y] (type 'end' if you have entered all points) ==> "
                )
                try:
                    if isinstance(ast.literal_eval(user_input), list):
                        ordered_coordinates.append(ast.literal_eval(user_input))
                        print(
                            f"Point number {i} : {ast.literal_eval(user_input)} saved \n"
                        ) if self.logs else None
                        i += 1

                except Exception as e:
                    print(e)
                    if user_input not in ["end", ""]:
                        print(
                            f"{user_input} is not a valid coordinnates or a valid end of input. If you have finished setting your coordinnates, type 'end' in the next prompt ==> "
                        )
        segments: List[Segment] = []
        no_to_all: bool = False
        for index, coordinates in enumerate(ordered_coordinates):
            point_1 = coordinates
            point_2 = (
                ordered_coordinates[0]
                if index == len(ordered_coordinates) - 1
                else ordered_coordinates[index + 1]
            )
            segment_id: str = ""
            if ordered_names is None:
                if not no_to_all:
                    segment_id = input(
                        f"\nSet your own segment_id (must be a unique string) "
                        f"between {point_1} and {point_2} or  type 'no' to "
                        f"generate one randomly (just for this segment) or "
                        f"'no to all' (for all segment): "
                    )
                if segment_id.lower().strip("'") == "no to all":
                    no_to_all = True
                if segment_id.lower().strip("'") == "no" or no_to_all:
                    segment_id = self.generate_unique_id("Segment")
            if len(ordered_names) != len(ordered_coordinates):
                raise UserInputError(
                    "Segment names ('ordered_names') has not the same length "
                    "as segment coordinates ('ordered_coordinates').\n"
                    "The number of segments must be equal to the "
                    "number of points/coordinates in any closed form."
                )
            if not segment_id:
                segment_id = ordered_names[index]
            segment: Segment = Segment(
                id=segment_id,
                label=ordered_names[index],
                points=[point_1, point_2],
                junction=None,
                length=self.compute_segment_length(
                    point_1=point_1,
                    point_2=point_2,
                ),
            )
            segments.append(segment)
        area: float = self.compute_area_from_coordinates(
            ordered_coordinates=ordered_coordinates
        )
        if self.verbose:
            LOGGER.info(
                f"Segments created: {segments}\nCorresponding area: {area} m²."
            )
        return segments, area

    def to_dict(self) -> Dict[str, Any]:
        """"""
        return {
            "structure_object_collection": self.structure_object_collection,  # Segment
            # "boundary_collection": self.boundary_collection,
            "archetype_collection": self.archetype_collection,
        }

    @staticmethod
    def compute_segment_length(
        point_1: Tuple[float, float], point_2: Tuple[float, float]
    ) -> float:
        """Compute euclidian distance between two point [x,y]

        Parameters
        ----------
        point_1: Tuple[float, float]
            Point no. 1
        point_2: Tuple[float, float]
            Point no. 2

        Returns
        -------
        segment_length: float:
            Euclidian distance between two point [x,y]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        segment_length: float = math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)
        return segment_length

    @staticmethod
    def compute_segment_length(
        point_1: Tuple[float, float], point_2: Tuple[float, float]
    ) -> float:
        """Compute euclidian distance between two point [x,y]

        Parameters
        ----------
        point_1: Tuple[float, float]
            Point no. 1
        point_2: Tuple[float, float]
            Point no. 2

        Returns
        -------
        segment_length: float:
            Euclidian distance between two point [x,y]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        x_1, y_1 = point_1
        x_2, y_2 = point_2
        segment_length: float = math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)
        return segment_length

    @staticmethod
    def compute_area_from_coordinates(
        ordered_coordinates: List[Tuple[float, float]],
    ) -> float:
        """Compute surface area from given coordinates (shape points)

        Parameters
        ----------
        ordered_coordinates: List[Tuple[float, float]]
            List of x,y coordinates [[x,y],[x1,y1...] in lambert93 (meters)
            used to describe the shape of a boundary in a plane reference
            coordinnates systems [0,0] is always one of the point of the
            boundary shape (the bottom left).
            Important: coordinates needs to be set in CLOCKWISE order.

        Returns
        -------
        area : float
            List of segments (without junction yet) in COLIBRI boundary segment format

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Ensure the polygon is closed by adding the first point to the end of the list
        copied_ordered_coordinates = copy.deepcopy(ordered_coordinates)
        copied_ordered_coordinates.append(copied_ordered_coordinates[0])
        area: float = 0.0
        for index, coordinates in enumerate(copied_ordered_coordinates[:-1]):
            x1, y1 = coordinates
            x2, y2 = copied_ordered_coordinates[index + 1]
            area += (x1 * y2) - (x2 * y1)
        area = abs(area) / 2.0
        return area