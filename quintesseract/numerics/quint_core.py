"""
The Quint: a single balanced quinary digit.

A Quint represents one of five symmetric states around zero:

    HIGH_DOWN = -2
    LOW_DOWN  = -1
    ZERO      =  0
    LOW_UP    = +1
    HIGH_UP   = +2

This is the atomic unit of the balanced quinary system. Every higher-level
construct (numbers, memory, registers, instructions) is built from sequences
of Quints.

Why balanced? In a standard positional system like decimal or binary, digits
range from 0 to base-1, and negative numbers require a separate sign bit or
two's complement scheme. In a balanced system, digits range symmetrically
around zero, and the sign of a number is simply the sign of its leading
non-zero digit. Negation becomes a per-digit operation: flip every digit
and you have negated the number. No sign bit, no special cases, no two's
complement.

The historical precedent for this is the Setun, a balanced ternary computer
built at Moscow State University in 1958. Knuth called balanced ternary
"perhaps the prettiest number system of all." This project asks: what
happens if you push the idea one base further?
"""

from enum import IntEnum


class Quint(IntEnum):
    """A single balanced quinary digit.

    Inherits from IntEnum, so Quints behave as integers in arithmetic
    contexts but render with their state names when printed.
    """

    HIGH_DOWN = -2
    LOW_DOWN = -1
    ZERO = 0
    LOW_UP = 1
    HIGH_UP = 2

    @classmethod
    def from_int(cls, value: int) -> "Quint":
        """Construct a Quint from an integer in [-2, 2].

        Raises ValueError if the value is out of range. This is a strict
        constructor: it does not silently truncate or wrap.
        """
        if not -2 <= value <= 2:
            raise ValueError(
                f"Quint value must be in range [-2, 2], got {value}. "
                f"For larger values, use QuintNumber."
            )
        return cls(value)

    def negate(self) -> "Quint":
        """Return the additive inverse of this Quint.

        Negation in balanced quinary is a per-digit operation. This is one
        of the elegant properties of balanced systems.
        """
        return Quint(-self.value)

    def __repr__(self) -> str:
        return f"Quint.{self.name}"