"""
Segment class, which represent the segment structure object.
"""

from typing import List, Optional, Union

from colibri.interfaces import StructureObject
from colibri.project_objects import LinearJunction, PunctualJunction
from colibri.utils.enums_utils import Roles, Units


class Segment(StructureObject):
    """Class representing a segment."""

    TYPE: str = "segment"
    DESCRIPTION: str = (
        "A segment describe the edge of a boundary, which is useful for "
        "representing the boundary geometrically and positioning boundaries "
        "relative to each other and/or the exterior."
    )

    def __init__(
        self,
        id: str,
        label: str,
        length: float,
        points: Optional[List[List[float]]] = None,
        junction: Optional[Union[LinearJunction, PunctualJunction]] = None,
    ) -> None:
        """Initialize a new Segment instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the segment.",
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
            description="Name/label of the segment, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.length = self.define_parameter(
            name="length",
            default_value=length,
            description="Length of a given segment of the boundary.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        self.points = self.define_parameter(
            name="points",
            default_value=points,
            description="Points' coordinates (x,y) forming a segment."
            "Examples: [[x1,y1], [x2,y2]].",
            format=List[List[float]],
            min=0,
            max=float("inf"),
            unit=Units.METER,
            attached_to=None,
            required=None,
        )
        self.junction = self.define_parameter(
            name="junction",
            default_value=junction,
            description="A linear junction connects one segment to another "
            "using 'nodes_type' and 'nodes_id' in order to find "
            "the nodes in nodes_collection of the project. "
            "Junctions allow multiple boundaries to be "
            "in contact."
            "Examples: {"
            "'nodes_type' : 'linear_junction',"
            "'nodes_id' : 'junction_64',"
            "}",
            format=Union[LinearJunction, PunctualJunction],
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )


if __name__ == "__main__":
    from colibri.config.constants import LOGGER
    from colibri.project_objects import LinearJunction

    linear_junction_1: LinearJunction = LinearJunction(
        id="mur_salon_sud_et_mur_salon_ouest_junction",
        label="Junction entre les murs du sud et de l'ouest du salon",
        type="linear_junction",
        type_id="mur_salon_sud_et_mur_salon_ouest_junction",
    )
    segment_1: Segment = Segment(
        id="mur_salon_sud_segment",
        label="Segment du mur du salon orienté sud",
        length=2.5,
        points=[[0, 0], [0, 2.5]],
        junction=linear_junction_1,
    )
    LOGGER.debug(segment_1)
