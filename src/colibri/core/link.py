"""
Link class to link one module to another.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from colibri.interfaces.module import Module


@dataclass
class Link:
    """Class representing a link from one module to another."""

    from_module: Optional[Module] = None
    from_field: Optional[str] = None
    to_module: Optional[Module] = None
    to_field: Optional[str] = None
