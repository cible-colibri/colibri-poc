"""
ProjectData class that construct the project data objects
for the `colibri` package.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from colibri.config.constants import (
    ARCHETYPE_COLLECTION,
    BOUNDARY_COLLECTION,
    COLLECTION,
    JUNCTION,
    NODE_COLLECTION,
    PROJECT,
    SEGMENTS,
    SPACE,
    SPACE_COLLECTION,
    TYPE,
    TYPE_ID,
)
from colibri.interfaces import (
    ElementObject,
    Module,
)
from colibri.project_objects import (
    Boundary,
    BoundaryCondition,
    LinearJunction,
    PunctualJunction,
    Segment,
    Space,
)
from colibri.utils.class_utils import (
    create_class_instance,
    get_class,
)
from colibri.utils.enums_utils import (
    ColibriObjectTypes,
    Units,
)


class ProjectData(Module):
    """Class representing the project's data (structure of the project)."""

    INSTANCE_NAME: str = "project_data"

    def __init__(self, name: str, data: Union[dict, Path]) -> None:
        """Initialize a new ProjectData instance."""
        super().__init__(name=name)
        self.project_file = data if isinstance(data, Path) is True else False
        self.project_data: dict = (
            self.read_project_file() if isinstance(data, Path) is True else data
        )
        if self.project_data:
            spaces: List[Space] = self.get_spaces()
            self.spaces: List[Space] = self.define_output(
                name="spaces",
                default_value=spaces,
                description="Spaces of the project.",
                format=List["Space"],
                min=None,
                max=None,
                unit=Units.UNITLESS,
                attached_to=None,
            )
            boundaries: List[Boundary] = self.get_boundaries()
            self.boundaries: List[Boundary] = self.define_output(
                name="boundaries",
                default_value=boundaries,
                description="Boundaries of the project.",
                format=List["Boundary"],
                min=None,
                max=None,
                unit=Units.UNITLESS,
                attached_to=None,
            )
            boundary_conditions: List[BoundaryCondition] = (
                self.get_boundary_conditions()
            )
            self.boundary_conditions: List[BoundaryCondition] = (
                self.define_output(
                    name="boundary_conditions",
                    default_value=boundary_conditions,
                    description="Boundary conditions of the project.",
                    format=List["BoundaryCondition"],
                    min=None,
                    max=None,
                    unit=Units.UNITLESS,
                    attached_to=None,
                )
            )

    def initialize(self) -> bool:
        return True

    def run(self, time_step: int, number_of_iterations: int) -> None: ...

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def save_time_step(self, time_step: int) -> None: ...

    def has_converged(
        self, time_step: int, number_of_iterations: int
    ) -> bool: ...

    def read_project_file(self):
        """Read the project file

        Returns
        -------
        project_data : dict
            Project/simulation/input data

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        with open(self.project_file, "r") as _file_descriptor:
            project_data: dict = json.load(_file_descriptor)
        return project_data

    def get_spaces(self) -> List[Space]:
        """Get spaces from the project/simulation/input data

        Returns
        -------
        spaces : List[Space]
            Spaces of the project/simulation/input data

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        spaces: List[Space] = []
        space_collection: List[dict] = self.project_data[PROJECT][
            NODE_COLLECTION
        ][SPACE_COLLECTION]
        for space_name, space_data in space_collection.items():
            space: Space = create_class_instance(
                class_name=SPACE,
                class_parameters=space_data,
                output_type=ColibriObjectTypes.PROJECT_OBJECT,
            )
            spaces.append(space)
        return spaces

    def get_boundaries(self) -> List[Boundary]:
        """Get boundaries from the project/simulation/input data

        Returns
        -------
        boundaries : List[Boundary]
            Boundaries of the project/simulation/input data

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        boundaries: List[Boundary] = []
        boundary_collection: List[dict] = []
        if BOUNDARY_COLLECTION in self.project_data[PROJECT]:
            boundary_collection = self.project_data[PROJECT][BOUNDARY_COLLECTION]
        else:
            return []

        for boundary_name, boundary_data in boundary_collection.items():
            segments_data: Dict[str, Any] = boundary_data.pop(SEGMENTS, [])
            boundary: Boundary = self.create_element_object(
                element_data=boundary_data,
                class_signature=Boundary,
            )
            boundary.segments = self.get_segments(
                segments_data=segments_data,
            )
            # Add boundary information to boundary object
            for boundary_object in boundary.object_collection:
                boundary_object.boundary = boundary
            # Add boundary/space information to space/boundary
            for space in self.spaces:
                if space.id in [boundary.side_1, boundary.side_2]:
                    space.boundaries.append(boundary)
                    boundary.spaces.append(space)
            boundaries.append(boundary)
        return boundaries

    def get_boundary_conditions(self) -> List[BoundaryCondition]:
        return []

    def get_segments(
        self,
        segments_data: List[Dict[str, Any]],
    ) -> List[Segment]:
        segments: List[Segment] = []
        for segment_data in segments_data:
            junction_data: Dict[str, Any] = segment_data.pop(JUNCTION, [])
            segment: Segment = create_class_instance(
                class_name=Segment.__name__,
                class_parameters=segment_data,
                output_type=ColibriObjectTypes.PROJECT_OBJECT,
            )
            if junction_data is not None:
                segment.junction = self.get_junction(
                    junction_data=junction_data,
                    segment_length=segment.length,
                )
            segments.append(segment)
        return segments

    def get_junction(
        self, junction_data: Dict[str, Any], segment_length: float
    ) -> Union[LinearJunction, PunctualJunction]:
        junction_type: str = junction_data[TYPE]
        junction_type_id: str = junction_data[TYPE_ID]
        junction_collection: str = f"{junction_type}_{COLLECTION}"
        junction_properties: Dict[str, Any] = self.project_data[PROJECT][
            NODE_COLLECTION
        ][junction_collection][junction_type_id]
        class_name: str = (
            LinearJunction.__name__
            if junction_type.split("_")[0] in LinearJunction.__name__.lower()
            else PunctualJunction.__name__
        )
        junction: Union[LinearJunction, PunctualJunction] = (
            create_class_instance(
                class_name=class_name,
                class_parameters=junction_properties,
                output_type=ColibriObjectTypes.PROJECT_OBJECT,
            )
        )
        junction.length = segment_length
        return junction

    def create_element_object(
        self,
        element_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        class_signature: Optional[Type] = None,
    ):
        is_element_data_list: bool = isinstance(element_data, list)
        is_element_data_dict: bool = isinstance(element_data, dict)
        if not (is_element_data_dict or is_element_data_list):
            return element_data
        if is_element_data_list:
            return [
                self.create_element_object(element_data=element)
                for element in element_data
            ]
        does_element_have_archetype: bool = (TYPE in element_data) and (
            TYPE_ID in element_data
        )
        if is_element_data_dict and does_element_have_archetype:
            archetype_data: Dict[str, Any] = self.get_archetype_data(
                object_data=element_data
            )
            class_name: str = element_data.get(TYPE).capitalize()
            class_parameters: Dict[str, Any] = {
                **archetype_data,
                **element_data,
            }
            class_signature: Type = get_class(
                class_name=class_name,
                output_type=ColibriObjectTypes.PROJECT_OBJECT,
            )
            if class_signature.__name__ == ElementObject.__name__:
                return class_signature.create_instance(
                    class_name=class_name,
                    fields={
                        parameter_name: self.create_element_object(
                            element_data=parameter_value
                        )
                        for parameter_name, parameter_value in class_parameters.items()
                    },
                )
            return class_signature(
                **{
                    parameter_name: self.create_element_object(
                        element_data=parameter_value
                    )
                    for parameter_name, parameter_value in class_parameters.items()
                }
            )
        if (
            is_element_data_dict
            and (not does_element_have_archetype)
            and (class_signature is not None)
        ):
            return class_signature(
                **{
                    parameter_name: self.create_element_object(
                        element_data=parameter_value
                    )
                    for parameter_name, parameter_value in element_data.items()
                }
            )

    def get_archetype_data(self, object_data: dict) -> Dict[str, Any]:
        """Get archetype data associated to an object

        Parameters
        ----------
        object_data : dict
            Object whose archetype data should be returned

        Returns
        -------
        archetype_data : Dict[str, Any]
            Archetype data of the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        archetype_type: str | None = object_data.get(TYPE, None)
        archetype_type_id: str | None = object_data.get(TYPE_ID, None)
        if (archetype_type is None) or (archetype_type_id is None):
            archetype_data: Dict[str, Any] = dict()
            return archetype_data
        archetype_type_key: str = f"{archetype_type}_{TYPE}s"
        archetype_data: Dict[str, Any] = self.project_data[PROJECT][
            ARCHETYPE_COLLECTION
        ][archetype_type_key][archetype_type_id]
        return archetype_data
