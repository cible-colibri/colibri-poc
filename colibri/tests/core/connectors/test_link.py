"""
This file tests the link.py module in dataclasses.
"""

import pytest

from colibri.core.connectors.link import Link
from colibri.core.models.model import Model
from colibri.models.hydronics.duct import Duct


@pytest.mark.short_test
def test_links() -> None:
    """Test the behavior of Link."""
    duct_1: Duct = Duct("duct_1")
    duct_2: Duct = Duct("duct_2")
    link_1: Link = Link(
        from_model=duct_1,
        from_variable="inlet_temperature",
        to_model=duct_2,
        to_variable="outlet_temperature",
    )
    link_2: Link = Link(duct_1, "inlet_flow_rate", duct_2, "outlet_flow_rate")
    assert isinstance(link_1, Link)
    assert isinstance(link_2, Link)
    assert hasattr(link_1, "from_model")
    assert hasattr(link_1, "from_variable")
    assert hasattr(link_1, "to_model")
    assert hasattr(link_1, "to_variable")
    assert isinstance(link_1.from_model, Model)
    assert (
        link_1.__str__()
        == "Link(from_model=Duct(name = 'duct_1'), from_variable='inlet_temperature', to_model=Duct(name = 'duct_2'), to_variable='outlet_temperature', index_from=None, index_to=None)"
    )
    assert link_1.__repr__() == link_1.__str__()
    assert link_2.__repr__() == link_2.__str__()


if __name__ == "__main__":
    test_links()
