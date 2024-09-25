"""
Tests for the `boundary_condition.py` module.
"""

from colibri.interfaces import StructureObject
from colibri.project_objects import BoundaryCondition


def test_boundary_condition() -> None:
    """Test the BoundaryCondition class"""
    boundary_condition_1: BoundaryCondition = BoundaryCondition(
        id="boundary-condition-1",
        label="External boundary condition",
    )
    assert isinstance(boundary_condition_1, BoundaryCondition) is True
    assert isinstance(boundary_condition_1, StructureObject) is True
    assert boundary_condition_1.id == "boundary-condition-1"


if __name__ == "__main__":
    test_boundary_condition()
