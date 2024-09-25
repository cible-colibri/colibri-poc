"""
Tests for the `building.py` module.
"""

from colibri.interfaces import StructureObject
from colibri.project_objects import Building


def test_building() -> None:
    """Test the Building class"""
    building_1 = Building(
        id="building-1",
        label="Building A",
    )
    assert isinstance(building_1, Building) is True
    assert isinstance(building_1, StructureObject) is True
    assert building_1.label == "Building A"

    building_2 = Building(
        id="building-2",
        label="Building B",
        height=16,
    )
    assert isinstance(building_2, Building) is True
    assert isinstance(building_2, StructureObject) is True
    assert building_2.label == "Building B"
    assert building_2.height == 16


if __name__ == "__main__":
    test_building()
