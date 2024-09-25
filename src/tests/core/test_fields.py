"""
Test for the `fields.py` module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Union

from colibri.core.fields import Field
from colibri.project_objects import (
    LinearJunction,
    PunctualJunction,
    Space,
)
from colibri.utils.enums_utils import (
    Roles,
    Units,
)

if TYPE_CHECKING:
    from colibri.modules import AcvExploitationOnly


def test_field() -> None:
    """Test the Variable class."""

    v_field: int = Field(
        name="v",
        default_value=42,
        description="V value.",
        format=float,
        min=None,
        max=None,
        role=Roles.PARAMETERS,
        unit=Units.UNITLESS,
        attached_to=None,
    )
    # TODO: assert v_field._get_format_representation() == "float"

    w_field: int = Field(
        name="w",
        default_value=dict(),
        description="W value.",
        format=Dict[str, float],
        min=None,
        max=None,
        role=Roles.PARAMETERS,
        unit=Units.UNITLESS,
        attached_to=None,
    )
    # TODO: assert w_field._get_format_representation() == "Dict[str, float]"

    x_field: int = Field(
        name="x",
        default_value=42,
        description="X value.",
        format=List[Space],
        min=None,
        max=None,
        role=Roles.PARAMETERS,
        unit=Units.UNITLESS,
        attached_to=None,
    )
    # TODO: assert x_field._get_format_representation() == "List[Space]"

    z_field: int = Field(
        name="z",
        default_value=42,
        description="Z value.",
        format=List["AcvExploitationOnly"],
        min=None,
        max=None,
        role=Roles.PARAMETERS,
        unit=Units.UNITLESS,
        attached_to=None,
    )
    # TODO: assert z_field._get_format_representation() == "List[AcvExploitationOnly]"


if __name__ == "__main__":
    test_field()
