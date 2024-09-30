"""
Archetype class, which is the parent class of each archetype
for the `colibri` package.
"""

from typing import Any, Dict

from colibri.mixins import ClassMixin, MetaFieldMixin
from colibri.utils.enums_utils import Units


class Archetype(ClassMixin, MetaFieldMixin):
    """Class representing a archetype object."""

    TYPE: str = "archetype"
    DESCRIPTION: str = (
        "An archetype groups objects' properties together " "to be reusable."
    )

    def __init__(
        self,
        id: str,
        label: str,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initialize a new Archetype instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the archetype object.",
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
            description="Name/label of the archetype, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    archetype: Archetype = Archetype(
        id="beton-1",
        label="béton 20cm",
    )
    LOGGER.debug(archetype)
