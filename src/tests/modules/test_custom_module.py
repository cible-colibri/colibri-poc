"""
Tests for the `custom_model.py` module.
"""

from colibri.modules import CustomModule


def test_custom_model() -> None:
    """Test the CustomModule class."""
    custom_model: CustomModule = CustomModule(
        name="custom_model-1",
    )
    assert isinstance(custom_model, CustomModule) is True
    assert custom_model.name == "custom_model-1"


if __name__ == "__main__":
    test_custom_model()
