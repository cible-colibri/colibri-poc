"""
StructureObject class, which is the parent class of each structure object
(project object which structures the project) for the `colibri` package.
"""

from colibri.mixins import ClassMixin, MetaFieldMixin


class StructureObject(ClassMixin, MetaFieldMixin):
    """Class representing a structure object, that is,
    a project object which structures the project."""

    def __init__(self) -> None:
        """Initialize a new StructureObject instance."""
        super().__init__()


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    structure_object: StructureObject = StructureObject()
    LOGGER.debug(structure_object)
    LOGGER.debug(structure_object._variables_metadata)
