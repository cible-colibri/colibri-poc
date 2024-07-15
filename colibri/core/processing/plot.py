"""
This file contains the Plot class.
"""

from dataclasses import dataclass

from colibri.core.model import Model


@dataclass
class Plot:
    """Class representing a plot."""
    name: str
    model: Model
    variable_name: str