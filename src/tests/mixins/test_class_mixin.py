"""
Tests for the `class_mixin.py` module.
"""

from colibri.mixins import ClassMixin


def test_class_mixin() -> None:
    """Test the ClassMixin class."""

    class NewClass(ClassMixin):
        def __init__(self, x: int, y: str):
            super().__init__()
            self.x = x
            self.y = y

    new_object: NewClass = NewClass(x=3, y="two")
    assert new_object.__str__() == new_object.__repr__()
    assert new_object.__str__() == "NewClass(x=3, y='two')"

    class NewClass2(ClassMixin):
        __slots__ = (
            "x",
            "y",
        )

        def __init__(self, x: int, y: str):
            super().__init__()
            self.x = x
            self.y = y

    new_object_2: NewClass2 = NewClass2(x=3, y="two")
    assert new_object_2.__str__() == new_object_2.__repr__()
    assert new_object_2.__str__() == "NewClass2(x=3, y='two')"

    class NewClass3(ClassMixin):
        def __init__(self):
            super().__init__()

    new_object_3: NewClass3 = NewClass3()
    assert new_object_3.__str__() == new_object_3.__repr__()
    assert new_object_3.__str__() == "NewClass3()"


if __name__ == "__main__":
    test_class_mixin()
