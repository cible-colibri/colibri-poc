"""
Link class to link one model to another.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from colibri.interfaces.model import Model


@dataclass
class Link:
    """Class representing a link from one model to another."""

    from_model: Optional[Model] = None
    from_field: Optional[str] = None
    to_model: Optional[Model] = None
    to_field: Optional[str] = None
