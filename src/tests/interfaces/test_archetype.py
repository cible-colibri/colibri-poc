"""
Tests for the `archetype.py` module.
"""

from colibri.interfaces import Archetype


def test_archetype() -> None:
    """Test the Archetype class."""
    archetype: Archetype = Archetype(
        id="beton-1",
        label="béton 20cm",
    )
    assert archetype.id == "beton-1"
    assert Archetype.to_scheme() == {
        "Archetype": {
            "id": {
                "description": "Unique identifier (ID) of the archetype object.",
                "format": "str",
                "min": None,
                "max": None,
                "unit": "-",
                "choices": None,
                "default": None,
            },
            "type": "archetype",
            "description": "An archetype groups objects' properties together to be reusable.",
            "label": {
                "description": "Name/label of the archetype, not used as id.",
                "format": "str",
                "min": None,
                "max": None,
                "unit": "-",
                "choices": None,
                "default": None,
            },
        }
    }


if __name__ == "__main__":
    test_archetype()
