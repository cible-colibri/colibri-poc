"""
Tests for the `enum_utils.py` module.
"""

from colibri.utils.enums_utils import ColibriObjectTypes


def test_enums() -> None:
    """Test the enums."""
    assert len([enum for enum in ColibriObjectTypes]) == 2
    assert ColibriObjectTypes.MODULE.value == "module"
    assert ColibriObjectTypes.PROJECT_OBJECT.value == "project_object"
