"""
Boundary class, which represent the Boundary structure object.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units

if TYPE_CHECKING:
    from colibri.project_objects import BoundaryObject, Segment, Space


class Boundary(StructureObject):
    """Class representing a boundary."""

    TYPE: str = "boundary"
    DESCRIPTION: str = (
        "A boundary is a two-sided plane surface delimiting spaces "
        "and/or the exterior.\n"
        "A boundary can be fictive or concrete (wall, floor, roof...)."
    )

    def __init__(
        self,
        id: str,
        label: str,
        side_1: str,
        side_2: str,
        area: float,
        azimuth: int,
        tilt: int,
        origin: Optional[Tuple[float, float, float]] = None,
        segments: Optional[List[Segment]] = None,
        object_collection: Optional[List[BoundaryObject]] = None,
        spaces: Optional[List[Space]] = None,
        **kwargs,
    ) -> None:
        """Initialize a new Boundary instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the boundary.",
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
            description="Name/label of the boundary (wall), not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.side_1 = self.define_parameter(
            name="side_1",
            default_value=side_1,
            description="Unique identifier (ID) of the space "
            "(or 'exterior' or 'ground' if not connected "
            "to a space or a bundary_condition node) "
            "onto which face 1 of the boundary is in contact.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.side_2 = self.define_parameter(
            name="side_2",
            default_value=side_2,
            description="Unique identifier (ID) of the space "
            "(or 'exterior' if not connected to a space) "
            "onto which face 2 of the boundary is in contact",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.area = self.define_parameter(
            name="area",
            default_value=area,
            description="Area of the boundary.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SQUARE_METER,
            attached_to=None,
            required=None,
        )
        self.azimuth = self.define_parameter(
            name="azimuth",
            default_value=azimuth,
            description="Normal orientation of the side 1 of the boundary.",
            format=int,
            min=0,
            max=359,
            unit=Units.DEGREE,
            attached_to=None,
            required=None,
        )
        self.tilt = self.define_parameter(
            name="tilt",
            default_value=tilt,
            description="Inclination of the boundary (wall) relative to the horizontal; "
            "0° : horizontal facing upwards, 90° : vertical, "
            "180° : horizontal facing downwards.",
            format=int,
            min=0,
            max=180,
            unit=Units.DEGREE,
            attached_to=None,
            required=None,
        )
        self.origin = self.define_parameter(
            name="origin_3d",
            default_value=origin,
            description="Origin (x,y,z) in the absolute reference of the "
            "first point of the first segment of the boundary."
            "It can be used to build the 3D model without using "
            "segment information for rebuilding anything.",
            format=Tuple[float, float, float],
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        if segments is None:
            segments: List[Segment] = []
        self.segments = self.define_parameter(
            name="segments",
            default_value=segments,
            description="Collection of segments forming the edges of the "
            "boundary or in case of a non 3D description "
            "linears of interest for modeling. "
            "Important: coordinates need to be set in CLOCKWISE "
            "order regarding side_1 of the boundary. The coordinates "
            "of segments are set in a 2D plane "
            "(boundaries are always planar) with a relative "
            "reference point, where the first point of the "
            "boundary is designated as x:0, y:0. "
            "If 3D is not used, the key 'points' is set to None "
            "and only 'length' is used. "
            "Examples :[ {'id' : 'arrete_1', "
            "'points' : [[x1,y1],[x2,y2]], "
            "'length' : 10, "
            "'junction' : {"
            "'nodes_type' : 'linear_junction',"
            "'nodes_id' : 'junction_64'} "
            "] "
            "Search for 'points', 'length', 'junction' "
            "to know more...",
            format=List["Segment"],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        if object_collection is None:
            object_collection: List[BoundaryObject] = []
        self.object_collection = self.define_parameter(
            name="object_collection",
            default_value=object_collection,
            description="Collection of objects associated to the boundary "
            "(windows, doors, emitters, inlets, ...).",
            format=List["BoundaryObject"],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        if spaces is None:
            spaces: List[Space] = []
        self.spaces = self.define_parameter(
            name="spaces",
            default_value=spaces,
            description="Spaces related to the boundary.",
            format=List["Space"],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        for key, value in kwargs.items():
            setattr(self, key, value)


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    boundary_1 = Boundary(
        id="mur_salon_sud_1",
        label="Mur salon sud",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=180,
        tilt=90,
        area=15.0,
        origin=None,
        segments=None,
    )
    LOGGER.debug(boundary_1)

    from colibri.project_objects import Segment

    segment_1: Segment = Segment(
        id="mur_salon_sud_segment",
        label="Segment du mur du salon orienté sud",
        length=2.5,
        points=[[0, 0], [0, 2.5]],
    )
    segments_1: List[Segment] = [segment_1]
    boundary_2 = Boundary(
        id="mur_salon_sud_1",
        label="Mur salon sud",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=180,
        tilt=90,
        area=15.0,
        origin=None,
        segments=segments_1,
    )
    LOGGER.debug(boundary_2)
