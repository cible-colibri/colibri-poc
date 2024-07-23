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

    def is_check_convergence(self):
        return (self.from_model.get_field(self.from_variable).check_convergence
                and self.to_model.get_field(self.to_variable).check_convergence)
