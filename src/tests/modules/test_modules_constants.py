"""
Tests for the `modules_constants.py` module.
"""

from colibri.modules.modules_constants import (
    SOLAR_CONSTANT_OF_THE_EARTH,
)


def test_modules_constants():
    """Test the constants for modules."""
    assert isinstance(SOLAR_CONSTANT_OF_THE_EARTH, float)
    assert SOLAR_CONSTANT_OF_THE_EARTH == 1367.0


if __name__ == "__main__":
    test_modules_constants()
