"""
LinearJunction class, which represent the linear junction structure object.
"""

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units


class LinearJunction(StructureObject):
    """Class representing a linear junction."""

    TYPE: str = "linear_junction"
    DESCRIPTION: str = (
        "A linear junction is used when boundaries are in contact on "
        "a segment and can be used for thermal bridges calculation or "
        "for the 3D structure of a project."
    )

    def __init__(
        self,
        id: str,
        label: str,
    ) -> None:
        """Initialize a new LinearJunction instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the linear junction.",
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
            description="Name/label of the linear junction, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    linear_junction_1: LinearJunction = LinearJunction(
        id="mur_salon_sud_et_mur_salon_ouest_junction",
        label="Junction entre les murs du sud et de l'ouest du salon",
    )
    LOGGER.debug(linear_junction_1)
