"""
This file contains the File class.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class File:
    name: str
    path: Path
    description: str = ""
