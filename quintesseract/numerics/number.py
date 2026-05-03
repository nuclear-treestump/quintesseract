"""
The QuintNumber: a multi-digit balanced quinary number.

A QuintNumber is a sequence of Quints representing a signed integer in
balanced quinary. Internally, digits are stored least-significant-first,
because carry propagation in addition naturally moves from low to high.
The string representation reverses this for human readability.

The interesting property of balanced quinary arithmetic is that carries
can be negative. In standard base-5, digits range 0 to 4, so 4 + 4 = 8,
which is "1 carry, 3 in this position." In balanced quinary, digits range
-2 to 2, so 2 + 2 = 4, which cannot fit in a single quint. Instead, it
becomes "1 carry, -1 in this position" because (1 * 5) + (-1) = 4.
Carries can be -1, 0, or +1, never larger.

This is implemented by a normalize step after addition: walk through the
digits low to high, and any digit outside [-2, 2] gets reduced by adding
or subtracting 5 and propagating the appropriate carry.
"""

from typing import List, Iterable
from quintesseract.numerics.quint_core import Quint


# The base of our number system. Named for clarity; this is 5.
BASE = 5


class QuintNumber:
    """A signed integer represented in balanced quinary.

    Digits are stored least-significant-first. The number 12 in balanced
    quinary is +1 * 25 + (-2) * 5 + 2 * 1 = 17... no wait, let me redo
    that example. 12 = 2 * 5 + 2, so digits least-significant-first are
    [HIGH_UP, HIGH_UP] (the 1s place is 2, the 5s place is 2).

    More interesting example: 7 = 2 * 5 + (-3)... but -3 is not a valid
    quint. So 7 must be represented as 1 * 25 + (-2) * 5 + 2, giving
    digits [HIGH_UP, HIGH_DOWN, LOW_UP] least-significant-first.

    In repr, this displays most-significant-first as "(+1)(-2)(+2)" with
    a decimal annotation.
    """

    def __init__(self, digits: Iterable[Quint]):
        """Initialize from an iterable of Quints, least-significant-first.

        Trailing zero digits (in the high positions) are stripped. The
        number zero is represented as an empty digit list, which displays
        as a single ZERO.
        """
        digit_list = list(digits)
        # Strip trailing (high-position) zeros
        while digit_list and digit_list[-1] == Quint.ZERO:
            digit_list.pop()
        self._digits: List[Quint] = digit_list

    @classmethod
    def from_int(cls, value: int) -> "QuintNumber":
        """Construct a QuintNumber from a Python integer.

        The conversion algorithm: repeatedly take value mod 5 to get a
        digit in [0, 4], then adjust to [-2, 2] by carrying when needed.
        If the digit comes out as 3, we use -2 and carry +1 to the next
        position. If it comes out as 4, we use -1 and carry +1.
        """
        if value == 0:
            return cls([])

        digits = []
        remaining = value
        while remaining != 0:
            # Standard mod operation gives [0, 4]
            digit = remaining % BASE
            remaining = remaining // BASE
            # Adjust to balanced range [-2, 2]
            if digit > 2:
                digit -= BASE
                remaining += 1
            digits.append(Quint(digit))

        return cls(digits)

    def to_int(self) -> int:
        """Convert this QuintNumber back to a Python integer."""
        total = 0
        for power, digit in enumerate(self._digits):
            total += digit.value * (BASE ** power)
        return total

    @property
    def digits(self) -> List[Quint]:
        """The digits, least-significant-first. Read-only view."""
        return list(self._digits)

    def negate(self) -> "QuintNumber":
        """Return the additive inverse.

        In balanced quinary, this is just per-digit negation. No two's
        complement, no sign bit flipping, no special cases.
        """
        return QuintNumber([d.negate() for d in self._digits])

    def __neg__(self) -> "QuintNumber":
        return self.negate()

    def __add__(self, other: "QuintNumber") -> "QuintNumber":
        """Add two QuintNumbers.

        The algorithm: pad both numbers to the same length with zeros,
        add digit-by-digit (carrying as needed), then normalize the
        result so all digits are back in [-2, 2].
        """
        if not isinstance(other, QuintNumber):
            return NotImplemented

        # Work in plain integers during addition so we can have
        # out-of-range values that get normalized at the end
        max_len = max(len(self._digits), len(other._digits))
        a = [d.value for d in self._digits] + [0] * (max_len - len(self._digits))
        b = [d.value for d in other._digits] + [0] * (max_len - len(other._digits))
        raw_sum = [a[i] + b[i] for i in range(max_len)]

        normalized = _normalize(raw_sum)
        return QuintNumber([Quint(d) for d in normalized])

    def __sub__(self, other: "QuintNumber") -> "QuintNumber":
        """Subtraction is addition of the negation."""
        if not isinstance(other, QuintNumber):
            return NotImplemented
        return self + other.negate()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuintNumber):
            return NotImplemented
        return self._digits == other._digits

    def __hash__(self) -> int:
        return hash(tuple(self._digits))

    def __repr__(self) -> str:
        if not self._digits:
            return "QuintNumber(0)"
        # Display most-significant-first
        parts = []
        for d in reversed(self._digits):
            sign = "+" if d.value >= 0 else "-"
            parts.append(f"({sign}{abs(d.value)})")
        return f"QuintNumber({''.join(parts)} = {self.to_int()})"

    def __str__(self) -> str:
        return str(self.to_int())


def _normalize(raw_digits: List[int]) -> List[int]:
    """Reduce a list of integers (potentially out of [-2, 2]) to balanced
    quinary form.

    This is the core arithmetic primitive. After adding two numbers
    digit-by-digit, individual digits can range from -4 to +4. We walk
    through low to high, and any digit outside [-2, 2] gets adjusted by
    adding or subtracting 5 (with corresponding carry of -1 or +1 to
    the next position).

    The maximum carry magnitude is 1, which is the property that makes
    this terminate cleanly and not require iteration.
    """
    digits = list(raw_digits)
    i = 0
    while i < len(digits):
        d = digits[i]
        if d > 2:
            # Too high: subtract 5, carry +1
            carry = (d + 2) // BASE  # how many times we need to subtract
            digits[i] = d - carry * BASE
            if i + 1 >= len(digits):
                digits.append(0)
            digits[i + 1] += carry
        elif d < -2:
            # Too low: add 5, carry -1
            carry = (-d + 2) // BASE
            digits[i] = d + carry * BASE
            if i + 1 >= len(digits):
                digits.append(0)
            digits[i + 1] -= carry
        i += 1

    # Strip trailing zeros
    while digits and digits[-1] == 0:
        digits.pop()

    return digits