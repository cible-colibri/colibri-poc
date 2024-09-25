"""
Tests for the `logging_utils.py` module.
"""

import pytest

from colibri.utils.logging_utils import initialize_logger


def test_initialize_logger() -> None:
    """Test the creation of the logger to write status messages

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
    logger_1 = initialize_logger()
    logger_2 = initialize_logger()
    assert logger_1 is logger_2
