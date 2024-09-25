"""
Tests for the `custom_model.py` module.
"""

from colibri.modules import CustomModel


def test_custom_model() -> None:
    """Test the CustomModel class."""
    custom_model: CustomModel = CustomModel(
        name="custom_model-1",
    )
    assert isinstance(custom_model, CustomModel) is True
    assert custom_model.name == "custom_model-1"


if __name__ == "__main__":
    test_custom_model()
