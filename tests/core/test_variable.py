# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import operator
import pytest

# ========================================
# Internal imports
# ========================================

from core.variable     import Variable
from utils.enums_utils import (
                                Roles,
                                Units,
                               )

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

@pytest.mark.short_test
def test_variable():
    a = Variable("a", 0, Roles.INPUTS)
    a.value = 42.2
    b = Variable("b", 0, Roles.INPUTS)
    b.value = 2
    c = Variable("c", 0, Roles.INPUTS)
    c.value = 2

    assert a + b == 44.2
    assert a + 1 == 43.2
    assert 1 + a == 43.2

    assert a - b == 40.2
    assert a - 1 == 41.2
    assert 1 - a == -41.2

    assert a * b == 84.4
    assert a * 2 == 84.4
    assert 42.2 * b == 84.4

    assert a / b  == 21.1
    assert a / 2 == 21.1
    assert 42.2 / b == 21.1

    assert operator.truediv(a, b) == 21.1
    assert operator.truediv(a, 2) == 21.1
    assert operator.truediv(42.2, b) == 21.1

    assert a > b
    assert not (b > a)

    assert c == b

    # TODO: add tests for all operators


@pytest.mark.short_test
def test_unit_conversion():
    a = Variable("a", 0, Roles.INPUTS)
    a.value = 42.2
    a.unit = Units.JOULE

    a_kJ = a.convert(Units.KILO_JOULE)
    assert a_kJ == a.value / 1000

    a.unit = Units.JOULE
    a_kWh = a.convert(Units.KILO_WATT_HOUR)
    assert a_kWh == pytest.approx(1.17222e-5, 1e-4)

    a.unit = Units.KILO_JOULE
    a_kWh = a.convert(Units.KILO_WATT_HOUR)
    assert a_kWh == pytest.approx(0.01172222, 1e-4)

    a.unit = Units.DEGREE_CELSIUS
    a_F = a.convert(Units.KELVIN)
    assert a_F == pytest.approx(315.35, 0.01)

    a.unit = Units.DEGREE_CELSIUS
    a_F = a.convert(Units.DEGREE_FAHRENHEIT)
    assert a_F == pytest.approx(107.96, 0.01)

    a.unit = Units.DEGREE_FAHRENHEIT
    a_F = a.convert(Units.KELVIN)
    assert a_F == pytest.approx(278.8167, 1e-4)


if __name__ == "__main__":
    test_variable()
    test_unit_conversion()
