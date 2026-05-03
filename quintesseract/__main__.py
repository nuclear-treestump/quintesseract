"""
An interactive REPL for the quintessence balanced quinary system.

Launches a prompt where you can type integer expressions and see them
evaluated in balanced quinary, peek and poke memory, inspect registers,
and watch the machine state evolve.

Run with: python -m quintessence
"""

import sys
from quintesseract.numerics.quint_core import Quint
from quintesseract.numerics.number import QuintNumber
from quintesseract.memory.memory_ops import Memory, RegisterFile


BANNER = """
quintessence v0.1.0 :: balanced quinary computing environment
states: HIGH_DOWN(-2) LOW_DOWN(-1) ZERO(0) LOW_UP(+1) HIGH_UP(+2)
type 'help' for commands, 'quit' to exit
"""

HELP = """
arithmetic:
    <expr>              evaluate an integer expression in balanced quinary
                        e.g.  7 + 5    -3 * 2 (no, mul not in v1)    100 - 37
                        operators supported: + - (negation also unary)

memory:
    peek <addr>         read memory cell at address
    poke <addr> <val>   write a quint value (-2..+2) to memory cell
    mem [start] [len]   dump memory (default: all 125 cells)

registers:
    reg                 dump all registers
    reg <name>          read a single register
    set <name> <val>    write a quint value to a register

other:
    help                show this message
    quit, exit          exit the REPL
"""

REGISTER_NAMES = ["A", "B", "C", "D"]


class REPL:
    def __init__(self):
        self.memory = Memory(size=125)
        self.registers = RegisterFile(REGISTER_NAMES)

    def run(self):
        print(BANNER)
        while True:
            try:
                line = input("quint> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            try:
                if not self.dispatch(line):
                    break
            except Exception as e:
                print(f"  error: {e}")

    def dispatch(self, line: str) -> bool:
        """Process one line of input. Returns False to exit."""
        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit"):
            return False
        if cmd == "help":
            print(HELP)
            return True
        if cmd == "peek":
            self._cmd_peek(parts[1:])
            return True
        if cmd == "poke":
            self._cmd_poke(parts[1:])
            return True
        if cmd == "mem":
            self._cmd_mem(parts[1:])
            return True
        if cmd == "reg":
            self._cmd_reg(parts[1:])
            return True
        if cmd == "set":
            self._cmd_set(parts[1:])
            return True

        # Otherwise, treat the line as an arithmetic expression
        self._eval_expression(line)
        return True

    def _cmd_peek(self, args):
        if len(args) != 1:
            print("  usage: peek <addr>")
            return
        addr = int(args[0])
        value = self.memory.peek(addr)
        print(f"  [{addr:04d}] = {value.value:+d} ({value.name})")

    def _cmd_poke(self, args):
        if len(args) != 2:
            print("  usage: poke <addr> <val>")
            return
        addr = int(args[0])
        val = int(args[1])
        quint = Quint.from_int(val)
        self.memory.poke(addr, quint)
        print(f"  [{addr:04d}] <- {quint.value:+d} ({quint.name})")

    def _cmd_mem(self, args):
        start = int(args[0]) if len(args) >= 1 else 0
        length = int(args[1]) if len(args) >= 2 else None
        print(self.memory.dump(start=start, length=length))

    def _cmd_reg(self, args):
        if not args:
            print(self.registers.dump())
        else:
            name = args[0].upper()
            value = self.registers.read(name)
            print(f"  {name}: {value.value:+d} ({value.name})")

    def _cmd_set(self, args):
        if len(args) != 2:
            print("  usage: set <name> <val>")
            return
        name = args[0].upper()
        val = int(args[1])
        quint = Quint.from_int(val)
        self.registers.write(name, quint)
        print(f"  {name} <- {quint.value:+d} ({quint.name})")

    def _eval_expression(self, line: str):
        """Evaluate a simple expression with + and - on integers,
        showing both the decimal result and the balanced quinary form.

        Deliberately does NOT use eval(). This is a hand-parsed
        expression of the form: term [(+|-) term]*
        where term is an optional minus followed by an integer.
        """
        result = _parse_and_eval(line)
        qn = QuintNumber.from_int(result)
        print(f"  decimal: {result}")
        print(f"  balanced quinary: {_format_digits(qn)}")
        print(f"  (round-trip check: {qn.to_int() == result})")


def _format_digits(qn: QuintNumber) -> str:
    """Render a QuintNumber as a most-significant-first digit string."""
    if not qn.digits:
        return "[ZERO]"
    parts = [f"{d.value:+d}" for d in reversed(qn.digits)]
    return "[" + " ".join(parts) + "]"


def _parse_and_eval(line: str) -> int:
    """Parse an expression like '7 + 5 - 3' into a Python int."""
    tokens = _tokenize(line)
    if not tokens:
        raise ValueError("empty expression")

    # First token must be a number (with optional unary minus)
    pos = 0

    def parse_number(p):
        sign = 1
        if tokens[p] == "-":
            sign = -1
            p += 1
        elif tokens[p] == "+":
            p += 1
        if p >= len(tokens):
            raise ValueError("expected number")
        try:
            value = int(tokens[p])
        except ValueError:
            raise ValueError(f"not a number: {tokens[p]!r}")
        return sign * value, p + 1

    value, pos = parse_number(pos)
    while pos < len(tokens):
        op = tokens[pos]
        pos += 1
        if op not in ("+", "-"):
            raise ValueError(f"expected operator, got {op!r}")
        if pos >= len(tokens):
            raise ValueError("expected number after operator")
        rhs, pos = parse_number(pos)
        if op == "+":
            value += rhs
        else:
            value -= rhs
    return value


def _tokenize(line: str):
    """Split a line into tokens, handling +/- as separate tokens."""
    out = []
    current = ""
    for ch in line:
        if ch.isspace():
            if current:
                out.append(current)
                current = ""
        elif ch in "+-":
            if current:
                out.append(current)
                current = ""
            out.append(ch)
        else:
            current += ch
    if current:
        out.append(current)
    return out


def main():
    REPL().run()


if __name__ == "__main__":
    main()