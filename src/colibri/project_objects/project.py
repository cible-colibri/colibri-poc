"""
Project class, which represent the Project structure object.
"""

from __future__ import annotations

from typing import Any, Dict

from colibri.interfaces import StructureObject
from colibri.utils.enums_utils import Roles, Units


class Project(StructureObject):
    """Class representing a project."""

    TYPE: str = "project"
    DESCRIPTION: str = "Project."

    def __init__(
        self,
        id: str,
        label: str,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initialize a new Building instance."""
        super().__init__()
        self.id = self.define_parameter(
            name="id",
            default_value=id,
            description="Unique identifier (ID) of the project.",
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
            description="Name/label of the project, not used as id.",
            format=str,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    project_1: Project = Project(
        id="project-1",
        label="Project A",
    )
    LOGGER.debug(project_1)
