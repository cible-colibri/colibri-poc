# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import dataclasses

# ========================================
# Internal imports
# ========================================
from math import floor
from operator import truediv, floordiv

from utils.enums_utils import Units

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

@dataclasses.dataclass
class Variable:
    name: str
    value: float = 0
    unit: Units = Units.UNITLESS
    description: str = "Sorry, no description yet."

    def __add__(self, val2):
        return self.value + val2
    __radd__ = __add__

    def __sub__(self, val2):
        return self.value - val2

    def __rsub__(self, val2):
        return val2 - self.value

    def __mul__(self, val2):
        if type(val2) == Variable: # why is this not required for + or / ???
            return self.value * val2.value
        else:
            return self.value * val2

    def __rmul__(self, val2):
        if type(val2) == Variable:
            return self.value * val2.value
        else:
            return self.value * val2

    #for now variables are scalar only, but this may change quickly if Anthony comes up with another smart idea
    # def __matmul__(self, val2):
    #     return self.value / val2

    def __truediv__(self, val2):
        return truediv(self.value, val2)
    def __rtruediv__(self, val2):
        return truediv(val2, self.value)

    def __floordiv__(self, val2):
        return floordiv(self.value, val2)
    def __rfloordiv__(self, val2):
        return floordiv(val2, self.value)

    def __mod__(self, val2):
        return self.value % val2
    def __rmod__(self, val2):
        return val2 % self.value

    def __divmod__(self, val2):
        return divmod(self.value, val2)
    def __rdivmod__(self, val2):
        return divmod(val2, self.value)

    def __pow__(self, val2):
        return pow(self.value, val2)
    def __rpow__(self, val2):
        return pow(val2, self.value)

    def __lshift__(self, val2):
        return self.value << val2
    def __rlshift__(self, val2):
        return val2 << self.value

    def __rshift__(self, val2):
        return self.value >> val2
    def __rrshift__(self, val2):
        return val2 >> self.value

    def __and__(self, val2):
        return self.value and val2
    def __rand__(self, val2):
        return val2 and self.value

    def __xor__(self, val2):
        return self.value or val2
    __rxor__ = __xor__

    def __or__(self, val2):
        return self.value or val2
    __ror__ = __or__

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return self.value

    def __abs__(self):
        return abs(self.value)

    def __invert__(self):
        return ~self.value

    # rich comparison methods
    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return not (self.value == other)

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

