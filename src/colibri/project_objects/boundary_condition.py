"""
BoundaryCondition class, which represent the boundary condition structure object.
"""

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units


class BoundaryCondition(StructureObject):
    """Class representing a boundary condition."""

    TYPE: str = "boundary_condition"
    DESCRIPTION: str = (
        "A boundary condition is used to impose boundary conditions "
        "(to a boundary, to a real network...)."
    )

    def __init__(
        self,
        id: str,
        label: str,
    ) -> None:
        """Initialize a new BoundaryCondition instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Identifier (ID) of the boundary condition.",
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
            description="Name/label of the boundary condition, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    boundary_condition_1: BoundaryCondition = BoundaryCondition(
        id="mur_salon_condition_exterieure",
        label="Condition extérieure mur salon",
    )
    LOGGER.debug(boundary_condition_1)
