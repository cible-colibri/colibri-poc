# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import json
import pathlib
import typing

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================

# Read a json file and return its data
def read_json_file(file_path: typing.Union[str, pathlib.Path], mode: str = 'r') -> dict:
    """Read a json file and return its data

    Parameters
    ----------
    file_path : typing.Union[str, pathlib.Path]
        Path to the file to be read
    mode : str ('r' by default)
        Mode in which the file is opened

    Returns
    -------
    data : dict
        Dictionary containing the data inside the json file

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    file_path = str(pathlib.Path(file_path).absolute())
    with open(file_path, mode) as _file_descriptor:
        data = json.load(_file_descriptor)
    return data


# Write a json file based on the given data
def write_json_file(file_path: typing.Union[str, pathlib.Path], data: typing.Any, mode: str = 'w') -> None:
    """Write a json file based on the given data

    Parameters
    ----------
    file_path : typing.Union[str, pathlib.Path]
        Path to the file to be read
    data : typing.Any
        Data to be saved into the json file
    mode : str ('w' by default)
        Mode in which the file is opened

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
    file_path = str(pathlib.Path(file_path).absolute())
    with open(file_path, mode) as _file_descriptor:
        json.dump(data, _file_descriptor)
