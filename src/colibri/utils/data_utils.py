"""
Helper functions when working with data types for the `colibri` package.
"""

import inspect
import math
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from colibri.config.constants import (
    COLIBRI,
    ENUM,
    FORWARD_REF,
    LOGGER,
    TYPING,
)


def are_dictionaries_equal(
    dict_1: Dict[str, Any],
    dict_2: Dict[str, Any],
    keys_to_be_excluded: Optional[List[str]] = None,
) -> bool:
    """Return True if both dictionaries are the same
    (totally or by excluding some keys), False otherwise

    Parameters
    ----------
     dict_1 : Dict[str, Any]
         First dictionary to be compared
     dict_2 : Dict[str, Any]
         Second dictionary to be compared
     keys_to_be_excluded : Optional[List[str]] = None
         Keys to be excluded from the comparison

    Returns
    -------
    bool
        True if both dictionaries are the same
        (totally or by excluding some keys), False otherwise

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    if keys_to_be_excluded is None:
        keys_to_be_excluded: List[str] = []
    # Check if the same keys are present in both dicts (excluding keys_to_be_excluded)
    # by intersection of keys in both dicts
    common_keys: Set[str] = set(dict_1.keys()) & set(dict_2.keys())
    if (len(common_keys) != len(dict_1.keys())) or (
        len(common_keys) != len(dict_2.keys())
    ):
        LOGGER.warning(
            "dict_1 and dict_2 have not the same amount of keys. The comparison will be only on common keys."
        )
    # Removing keys to exclude
    keys_to_check: Set[str] = common_keys - set(keys_to_be_excluded)
    return all(dict_1[key] == dict_2[key] for key in keys_to_check)


def turn_format_to_string(field_format: Any) -> str:
    """Return the string representation of the format

    Parameters
    ----------
    field_format: Any
        Format of a field

    Returns
    -------
    str
        String representation of the format

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    format_representation: str = repr(field_format)
    has_typing_types: bool = TYPING in format_representation
    has_colibri_types: bool = COLIBRI in format_representation
    has_forward_ref_types: bool = FORWARD_REF in format_representation
    if inspect.isclass(field_format) and issubclass(field_format, Enum):
        return ENUM
    if (
        (not has_typing_types)
        and (not has_colibri_types)
        and (not has_forward_ref_types)
        and (isinstance(field_format, str))
    ):
        return field_format
    if (
        (not has_typing_types)
        and (not has_colibri_types)
        and (not has_forward_ref_types)
    ):
        return field_format.__name__
    if has_typing_types:
        format_representation = format_representation.replace(f"{TYPING}.", "")
    if has_forward_ref_types:
        pattern: str = f"{FORWARD_REF}\('(\w+)'\)"
        return re.sub(pattern, r"\1", format_representation)
    if has_colibri_types:
        pattern: str = r"(\w+)\[(.*?)\]"
        matches: Union[List[str], None] = re.match(
            pattern, format_representation
        )
        if matches is None:
            pattern = r"\b(?:\w+\.)*(\w+)\b"
            matches = re.findall(pattern, format_representation)
            return matches[-1]
        prefix = matches.group(1)
        inside_brackets = matches.group(2)
        pattern = r"(?:\w+\.)*(\w+)"
        matches = re.findall(pattern, inside_brackets)
        return f"{prefix}[" + ", ".join(matches) + "]"
    return format_representation


def turn_max_min_to_string(max_or_min: Any) -> str:
    """Return the string representation of the max or min

    Parameters
    ----------
    max_or_min: Any
        Max or min

    Returns
    -------
    str
        String representing of the max or min

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    if (max_or_min is not None) and (math.isinf(max_or_min) is True):
        return repr(max_or_min)
    return max_or_min
