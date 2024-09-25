"""
PunctualJunction class, which represent the punctual junction structure object.
"""

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units


class PunctualJunction(StructureObject):
    """Class representing a punctual junction."""

    TYPE: str = "punctual_junction"
    DESCRIPTION: str = (
        "A punctual junction is used when objects are linked"
        " through an assimilated 'single point connexion'.\n"
        "Example: a pipe with an air vent."
    )

    def __init__(
        self,
        id: str,
        label: str,
    ) -> None:
        """Initialize a new PunctualJunction instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the punctual junction.",
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
            description="Name/label of the punctual junction, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    punctual_junction_1: PunctualJunction = PunctualJunction(
        id="mur_salon_sud_et_mur_salon_ouest_et_plancher_junction",
        label="Junction entre les murs du sud et de l'ouest du salon avec le plancher",
    )
    LOGGER.debug(punctual_junction_1)
