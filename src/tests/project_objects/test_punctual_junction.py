"""
Tests for the `punctual_junction.py` module.
"""

import pytest

from colibri.interfaces import StructureObject
from colibri.project_objects import PunctualJunction


def test_punctual_junction() -> None:
    """Test the PunctualJunction class"""
    punctual_junction_1: PunctualJunction = PunctualJunction(
        id="punctual-junction-1",
        label="Punctual junction",
    )
    assert isinstance(punctual_junction_1, PunctualJunction) is True
    assert isinstance(punctual_junction_1, StructureObject) is True
    assert punctual_junction_1.id == "punctual-junction-1"


if __name__ == "__main__":
    test_punctual_junction()
