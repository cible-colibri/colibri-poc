"""
This file contains the Plot class.
"""

from dataclasses import dataclass

from colibri.core.models.model import Model


@dataclass
class Plot:
    name: str
    model: Model
    variable_name: str
