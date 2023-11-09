# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib
import setuptools

# ========================================
# External CSTB imports
# ========================================


# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================

ABOUT = dict()
directory_path = pathlib.Path(__file__).parent
with open(directory_path / "colibri" / "__project_information__.py", "r", encoding="utf-8") as _file_descriptor:
    exec(_file_descriptor.read(), ABOUT)

with open(directory_path / "README.md", "r", encoding="utf-8") as _file_descriptor:
    README = _file_descriptor.read()

# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================


# ========================================
# Scripts
# ========================================

setuptools.setup(
    name=ABOUT["__package_name__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    keywords=["colibri"],
    long_description=README,
    long_description_content_type="text/markdown",
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    platforms=["Linux", "Windows"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "jsonschema",
    ],
    zip_safe=False,
    extras_require={
        "dev":  [
            "jsonschema",
            "pytest-cov",
        ],
        "doc":  [
            "Sphinx",
        ],
        "test": [
            "pytest-cov",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
    ],
    project_urls={
        "Source": "https://scm.cstb.fr/dee/colibri",
    },
)
