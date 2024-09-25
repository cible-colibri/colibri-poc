"""
Tests for the `data_utils.py` module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Union

from colibri.project_objects import (
    LinearJunction,
    PunctualJunction,
    Space,
)
from colibri.utils.data_utils import (
    are_dictionaries_equal,
    turn_format_to_string,
    turn_max_min_to_string,
)

if TYPE_CHECKING:
    from colibri.modules import AcvExploitationOnly


def test_are_dictionaries_equal() -> None:
    """Test the are_dictionaries_equal function."""
    dict_1: Dict[str, Any] = {
        "a": 3,
        "b": "c",
        "d": 3,
    }
    dict_2: Dict[str, Any] = {
        "a": 3,
        "b": "c",
        "d": 4,
    }
    assert are_dictionaries_equal(dict_1=dict_1, dict_2=dict_2) is False
    assert (
        are_dictionaries_equal(
            dict_1=dict_1, dict_2=dict_2, keys_to_be_excluded=["d"]
        )
        is True
    )
    dict_1: Dict[str, Any] = {
        "a": 3,
        "b": "c",
        "d": 3,
    }
    dict_2: Dict[str, Any] = {
        "a": 3,
        "b": "c",
        "d": 4,
        "e": 6,
    }
    assert (
        are_dictionaries_equal(
            dict_1=dict_1, dict_2=dict_2, keys_to_be_excluded=["d"]
        )
        is True
    )


def test_turn_format_to_string() -> None:
    """Test the turn_format_to_string function ."""

    assert turn_format_to_string(field_format=str) == "str"
    assert turn_format_to_string(field_format=float) == "float"
    assert (
        turn_format_to_string(field_format=Dict[str, float])
        == "Dict[str, float]"
    )
    assert turn_format_to_string(field_format=List[Space]) == "List[Space]"
    assert (
        turn_format_to_string(
            field_format=Union[LinearJunction, PunctualJunction]
        )
        == "Union[LinearJunction, PunctualJunction]"
    )
    assert (
        turn_format_to_string(field_format=List["AcvExploitationOnly"])
        == "List[AcvExploitationOnly]"
    )


def test_turn_max_min_to_string() -> None:
    """Test the turn_max_min_to_string function ."""

    assert turn_max_min_to_string(max_or_min=0) == 0
    assert turn_max_min_to_string(max_or_min=None) is None
    assert turn_max_min_to_string(max_or_min=-1) == -1
    assert turn_max_min_to_string(max_or_min=44) == 44
    assert turn_max_min_to_string(max_or_min=float("inf")) == "inf"
