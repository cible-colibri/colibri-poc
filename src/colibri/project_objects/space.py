"""
Space class, which represent the Space structure object.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units

if TYPE_CHECKING:
    from colibri.project_objects import Boundary


class Space(StructureObject):
    """Class representing a space."""

    TYPE: str = "space"
    DESCRIPTION: str = "A space is a continuous volume delimited by boundaries."

    def __init__(
        self,
        id: Optional[str],
        label: Optional[str],
        boundaries: Optional[List[Boundary]] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initialize a new Space instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the space.",
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
            description="Name/label of the space (room), not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        if boundaries is None:
            boundaries: List[Boundary] = []
        self.boundaries = self.define_parameter(
            name="boundaries",
            default_value=boundaries,
            description="Boundaries related to the space.",
            format=List["Boundary"],
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

    space_1 = Space(
        id="living_room_1",
        label="salon",
    )
    LOGGER.debug(space_1)

    from colibri.project_objects import Boundary, Segment

    segment_1: Segment = Segment(
        id="mur_salon_sud_segment",
        label="Segment du mur du salon orienté sud",
        length=2.5,
        points=[[0, 0], [0, 2.5]],
    )
    segments: List[Segment] = [segment_1]
    boundary_1 = Boundary(
        id="mur_salon_sud_1",
        label="Mur salon sud",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=180,
        tilt=90,
        area=15.0,
        origin=None,
        segments=segments,
    )
    boundaries: List[Boundary] = [boundary_1]
    space_2 = Space(
        id="living_room_1",
        label="salon",
        boundaries=boundaries,
    )
    LOGGER.debug(space_2)
