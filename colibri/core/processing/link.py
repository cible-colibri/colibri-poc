"""
This file contains the Link class.
"""

from dataclasses import dataclass
from typing import Optional

from colibri.core.model import Model


@dataclass
class Link:
    from_model: Optional[Model] = None
    from_variable: Optional[str] = None
    to_model: Optional[Model] = None
    to_variable: Optional[str] = None
    # zero-based index if source of link is a vector
    index_from: Optional[int] = None
    # zero-based index if target of link is a vector
    index_to: Optional[int] = None