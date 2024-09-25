"""
BoundaryObject class, which is the parent class of each boundary object
(project object which is associated to a boundary) for the `colibri` package.
"""

from typing import Any, Dict

from colibri.mixins import ClassMixin, MetaFieldMixin
from colibri.utils.enums_utils import Units


class BoundaryObject(ClassMixin, MetaFieldMixin):
    """Class representing a boundary object, that is,
    a project object which is associated to a boundary."""

    TYPE: str = "boundary_object"
    DESCRIPTION: str = "A boundary object is an object attached to a boundary."

    def __init__(
        self,
        id: str,
        label: str,
        type: str,
        type_id: str,
        x_relative_position: float,
        y_relative_position: float,
        on_side: str,
        z_relative_position: float = 0.0,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initialize a new BoundaryObject instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the boundary object.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.label = self.define_parameter(
            name="label",
            default_value=label,
            description="Name/label of the boundary object, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.type = self.define_parameter(
            name="type",
            default_value=type,
            description="Type of the boundary object (e.g., window) "
            "according to archetype_collection.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.type_id = self.define_parameter(
            name="type_id",
            default_value=type_id,
            description="Unique identifier (ID) of the associated archetype "
            "object, which stores intrinsic properties of the "
            "boundary object.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.x_relative_position = self.define_parameter(
            name="x_relative_position",
            default_value=x_relative_position,
            description="Relative x position of the object on the "
            "side (plane referential) of the boundary.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        self.y_relative_position = self.define_parameter(
            name="y_relative_position",
            default_value=y_relative_position,
            description="Relative y position of the object on the affected "
            "side (plane referential) of the boundary.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        self.z_relative_position = self.define_parameter(
            name="z_relative_position",
            default_value=z_relative_position,
            description="Relative z-depth position of the object compared to "
            "the affected side (plane referential) of the boundary. "
            "By default 0 but can be used when something is not really exactly "
            "on one of the two side of the boundary",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        self.on_side = self.define_parameter(
            name="on_side",
            default_value=on_side,
            description="Side of the boundary where the object is located:\n"
            "- 'side_1';\n"
            "- 'side_2';\n"
            "- 'side_1_to_side_2': Element is connected to both "
            "face and make a hole/tunnel between them "
            "(for example: holes, windows, etc.). "
            "The direction of integration of the object is from "
            "side 1 to side 2;\n"
            "- 'side_2_to_side_1': Element is connected to both "
            "face and make a hole/tunnel between them "
            "(for example: holes, windows, etc.). "
            "The direction of integration of the object is from "
            "side 2 to side 1.\n",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    boundary_object: BoundaryObject = BoundaryObject(
        id="window_2",
        label="South kitchen window",
        type="window",
        type_id="typical_window",
        x_relative_position=1.0,
        y_relative_position=1.0,
        z_relative_position=0.0,
        on_side="side_1_to_side_2",
    )
    LOGGER.debug(boundary_object)
