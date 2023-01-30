from operator import truediv

import pytest

from core.variable import Variable


def test_variable():
    a = Variable("a")
    a.value = 42.2
    b = Variable("b")
    b.value = 2

    c = Variable("c")
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

    assert truediv(a,b) == 21.1
    assert truediv(a,2) == 21.1
    assert truediv(42.2,b) == 21.1

    assert a > b
    assert not (b > a)

    assert c == b

    # TODO: add tests for all operators
