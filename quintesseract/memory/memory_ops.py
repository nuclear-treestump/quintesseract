"""
Memory and registers: the storage substrate for the balanced quinary machine.

This is where the project transitions from "a number system" to "a
computational substrate." Memory is an array of quints addressed by quint
numbers. Registers are named single-cell locations.

For v1, memory is a fixed-size flat array. Each cell holds a single Quint
(not a QuintNumber), which is the natural unit of storage in this system,
analogous to how a byte is the natural unit of storage in a byte-addressed
machine. Multi-quint values are stored across consecutive cells.

The PEEK and POKE operations are deliberately named for the Commodore 64
heritage we are honoring. On a C64, PEEK(addr) read a byte from memory and
POKE addr, value wrote one. Here, peek reads a quint and poke writes one.
"""

from typing import Dict, List
from quintesseract.numerics.quint_core import Quint
from quintesseract.numerics.number import QuintNumber


class Memory:
    """A fixed-size array of Quints, addressed by integer or QuintNumber.

    Default size of 125 cells gives you the address range [0, 124], which
    in balanced quinary is exactly three digits worth of address space
    (5^3 = 125). This is small but not insultingly so, and it has the
    pleasing property of being a round number in our native base.
    """

    def __init__(self, size: int = 125):
        if size <= 0:
            raise ValueError(f"Memory size must be positive, got {size}")
        self._size = size
        self._cells: List[Quint] = [Quint.ZERO] * size

    @property
    def size(self) -> int:
        return self._size

    def _resolve_address(self, address) -> int:
        """Accept either a Python int or a QuintNumber as an address."""
        if isinstance(address, QuintNumber):
            address = address.to_int()
        if not isinstance(address, int):
            raise TypeError(
                f"Address must be int or QuintNumber, got {type(address).__name__}"
            )
        if not 0 <= address < self._size:
            raise IndexError(
                f"Address {address} out of range [0, {self._size})"
            )
        return address

    def peek(self, address) -> Quint:
        """Read the Quint at the given address."""
        return self._cells[self._resolve_address(address)]

    def poke(self, address, value: Quint) -> None:
        """Write a Quint to the given address."""
        if not isinstance(value, Quint):
            raise TypeError(
                f"Memory cells hold Quints, got {type(value).__name__}. "
                f"Use Quint.from_int() if you have a raw integer."
            )
        self._cells[self._resolve_address(address)] = value

    def dump(self, start: int = 0, length: int = None) -> str:
        """Produce a human-readable dump of memory contents.

        Format mimics classic memory dumps: address followed by a row of
        cell values. Each row holds 5 cells (one quinary 'group'), which
        keeps the layout natural for the base.
        """
        if length is None:
            length = self._size - start
        end = min(start + length, self._size)

        lines = []
        for row_start in range(start, end, 5):
            row = self._cells[row_start:min(row_start + 5, end)]
            cell_str = "  ".join(f"{c.value:+d}" for c in row)
            lines.append(f"{row_start:04d}:  {cell_str}")
        return "\n".join(lines)


class RegisterFile:
    """A named collection of single-Quint storage locations.

    Registers in this v1 are single-Quint cells, like memory cells. In
    later versions, registers may grow to hold full QuintNumbers, but
    starting with single-quint registers keeps the model consistent
    with memory.
    """

    def __init__(self, names: List[str]):
        self._registers: Dict[str, Quint] = {name: Quint.ZERO for name in names}

    def read(self, name: str) -> Quint:
        if name not in self._registers:
            raise KeyError(f"No such register: {name!r}")
        return self._registers[name]

    def write(self, name: str, value: Quint) -> None:
        if name not in self._registers:
            raise KeyError(f"No such register: {name!r}")
        if not isinstance(value, Quint):
            raise TypeError(f"Registers hold Quints, got {type(value).__name__}")
        self._registers[name] = value

    def dump(self) -> str:
        lines = []
        for name, value in self._registers.items():
            lines.append(f"  {name}: {value.value:+d} ({value.name})")
        return "\n".join(lines)