"""
quintessence: a balanced quinary computing environment.

A learning project that asks: what if we built a computer around a
five-state, sign-symmetric digit instead of a binary one?

Layer 1 (this release): Number system
    - Quint: the single-digit primitive
    - QuintNumber: multi-digit signed integers with full arithmetic
    - Memory: a quint-addressed storage array
    - RegisterFile: named single-quint storage locations

Future layers will add an instruction set, a virtual machine, an
assembler, and eventually a BASIC-like interactive environment.

The historical inspiration is the Setun, a balanced ternary computer
built in 1958 at Moscow State University. This project pushes that idea
one base further into territory that, as far as I know, has never been
implemented.
"""

from quintesseract.numerics.quint_core import Quint
from quintesseract.numerics.number import QuintNumber
from quintesseract.memory.memory_ops import Memory, RegisterFile

__version__ = "0.1.0"
__all__ = ["Quint", "QuintNumber", "Memory", "RegisterFile"]