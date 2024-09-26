"""CircularEconomy interface (IM_7)."""

import abc

from colibri.interfaces.model import Model
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class CircularEconomy(Model, metaclass=abc.ABCMeta):
    """Class representing a circular economy interface."""

    def __init__(
        self,
        name: str,
        circularity_score: float,
    ) -> None:
        """Initialize a new CircularEconomy instance."""
        super().__init__(name=name)
        self.circularity_score = self.define_output(
            name="circularity_score",
            default_value=circularity_score,
            description="Score de circularity.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.UNITLESS,
            attached_to=Attachment(
                category=ColibriProjectObjects.PROJECT,
            ),
        )
