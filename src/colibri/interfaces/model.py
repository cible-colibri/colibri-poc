"""
Class Model, which is the parent class of each model for the `colibri` package.
"""

from __future__ import annotations

import abc
import copy
from typing import TYPE_CHECKING, Optional, TypeVar, Union

from colibri.config.constants import SERIES_EXTENSION_NAME
from colibri.core.fields import Field
from colibri.core.link import Link
from colibri.mixins import ClassMixin, MetaFieldMixin
from colibri.utils.enums_utils import Roles

if TYPE_CHECKING:
    from colibri.core.project_orchestrator import ProjectOrchestrator

T = TypeVar("T")


class Model(ClassMixin, MetaFieldMixin):
    """Class representing an abstract model (interface for a concrete model)."""

    def __init__(
        self, name: str, project: Optional[ProjectOrchestrator] = None
    ) -> None:
        """Initialize a new Model instance

        Parameters
        ----------
        name: str
            Name of the model
        project : Optional[ProjectOrchestrator] = None
            Project from which the model belongs to

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        super().__init__()
        self.name = name
        self.project = project

    @abc.abstractmethod
    def initialize(self) -> None: ...

    @abc.abstractmethod
    def post_initialize(self) -> None: ...

    @abc.abstractmethod
    def run(self, time_step: int, number_of_iterations: int) -> None: ...

    @abc.abstractmethod
    def end_iteration(self, time_step: int) -> None: ...

    @abc.abstractmethod
    def end_time_step(self, time_step: int) -> None: ...

    @abc.abstractmethod
    def end_simulation(self, time_step: int) -> None: ...

    def save_time_step(self, time_step: int) -> None:
        """Save the output fields' value for the given time step

        Parameters
        ----------
        time_step : int
            Time step

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        for field in self.get_fields(role=Roles.OUTPUTS):
            getattr(self, f"{field.name}{SERIES_EXTENSION_NAME}")[time_step] = (
                copy.deepcopy(getattr(self, field.name))
            )

    def get_field(self, name: str) -> Union[Field, None]:
        """Get a specific field of the model by its name

        Parameters
        ----------
        name : str
            Name of the field to be retrieved

        Returns
        -------
        Union[Variable, None]
            Variable if it exists, None otherwise

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        return self._fields_metadata.get(name, None)

    def is_field_linked(self, field_name: str) -> bool:
        """Is the model's field already linked (to another model's field)

        Parameters
        ----------
        field_name : str
            Name of the field to be checked for a link

        Returns
        -------
        True if the model's field is already linked, False otherwise

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if not self.project:
            return False
        for link in self.project.links:
            if (link.to_model == self) and (link.to_field == field_name):
                return True
        return False

    def get_link(self, field_name: str) -> Link | None:
        """Return the link (if it exists) associated to the model's field

        Parameters
        ----------
        field_name : str
            Name of the field to be checked for a link

        Returns
        -------
        Link | None
            Link associated to the model's field if it exists,
            None otherwise

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        if not self.project:
            return None
        for link in self.project.links:
            if (link.to_model == self) and (link.to_field == field_name):
                return link
        return None
