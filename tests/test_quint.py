"""Tests for the quintessence balanced quinary system."""

import unittest
from quintesseract import Quint, QuintNumber, Memory, RegisterFile


class TestQuint(unittest.TestCase):
    def test_states(self):
        self.assertEqual(Quint.HIGH_DOWN.value, -2)
        self.assertEqual(Quint.LOW_DOWN.value, -1)
        self.assertEqual(Quint.ZERO.value, 0)
        self.assertEqual(Quint.LOW_UP.value, 1)
        self.assertEqual(Quint.HIGH_UP.value, 2)

    def test_from_int_valid(self):
        for v in range(-2, 3):
            self.assertEqual(Quint.from_int(v).value, v)

    def test_from_int_out_of_range(self):
        with self.assertRaises(ValueError):
            Quint.from_int(3)
        with self.assertRaises(ValueError):
            Quint.from_int(-3)

    def test_negate(self):
        self.assertEqual(Quint.HIGH_UP.negate(), Quint.HIGH_DOWN)
        self.assertEqual(Quint.LOW_UP.negate(), Quint.LOW_DOWN)
        self.assertEqual(Quint.ZERO.negate(), Quint.ZERO)


class TestQuintNumberRoundTrip(unittest.TestCase):
    """Every integer in a wide range should survive a round-trip
    through QuintNumber."""

    def test_round_trip_small(self):
        for n in range(-100, 101):
            with self.subTest(n=n):
                self.assertEqual(QuintNumber.from_int(n).to_int(), n)

    def test_round_trip_medium(self):
        for n in [-12345, -1000, -125, -7, 0, 7, 125, 1000, 12345]:
            with self.subTest(n=n):
                self.assertEqual(QuintNumber.from_int(n).to_int(), n)

    def test_round_trip_large(self):
        for n in [10**9, -(10**9), 5**20, -(5**20)]:
            with self.subTest(n=n):
                self.assertEqual(QuintNumber.from_int(n).to_int(), n)

    def test_zero(self):
        z = QuintNumber.from_int(0)
        self.assertEqual(z.to_int(), 0)
        self.assertEqual(z.digits, [])


class TestQuintNumberArithmetic(unittest.TestCase):
    def test_addition_simple(self):
        for a in range(-50, 51):
            for b in range(-50, 51):
                with self.subTest(a=a, b=b):
                    qa = QuintNumber.from_int(a)
                    qb = QuintNumber.from_int(b)
                    self.assertEqual((qa + qb).to_int(), a + b)

    def test_subtraction_simple(self):
        for a in range(-50, 51):
            for b in range(-50, 51):
                with self.subTest(a=a, b=b):
                    qa = QuintNumber.from_int(a)
                    qb = QuintNumber.from_int(b)
                    self.assertEqual((qa - qb).to_int(), a - b)

    def test_negation(self):
        for n in range(-100, 101):
            with self.subTest(n=n):
                self.assertEqual((-QuintNumber.from_int(n)).to_int(), -n)

    def test_addition_large(self):
        a = 12345
        b = 67890
        qa = QuintNumber.from_int(a)
        qb = QuintNumber.from_int(b)
        self.assertEqual((qa + qb).to_int(), a + b)

    def test_subtraction_to_zero(self):
        n = QuintNumber.from_int(42)
        self.assertEqual((n - n).to_int(), 0)
        self.assertEqual((n - n).digits, [])

    def test_carry_propagation(self):
        """2 + 2 should require a carry: 4 = 1*5 + (-1) = [LOW_DOWN, LOW_UP]"""
        result = QuintNumber.from_int(2) + QuintNumber.from_int(2)
        self.assertEqual(result.to_int(), 4)
        self.assertEqual(result.digits, [Quint.LOW_DOWN, Quint.LOW_UP])

    def test_equality(self):
        self.assertEqual(QuintNumber.from_int(7), QuintNumber.from_int(7))
        self.assertNotEqual(QuintNumber.from_int(7), QuintNumber.from_int(8))


class TestQuintNumberRepresentation(unittest.TestCase):
    def test_repr_includes_decimal(self):
        n = QuintNumber.from_int(42)
        self.assertIn("42", repr(n))

    def test_str_is_decimal(self):
        self.assertEqual(str(QuintNumber.from_int(42)), "42")
        self.assertEqual(str(QuintNumber.from_int(-7)), "-7")
        self.assertEqual(str(QuintNumber.from_int(0)), "0")


class TestMemory(unittest.TestCase):
    def test_default_size(self):
        m = Memory()
        self.assertEqual(m.size, 125)

    def test_initial_zeros(self):
        m = Memory(size=10)
        for i in range(10):
            self.assertEqual(m.peek(i), Quint.ZERO)

    def test_poke_and_peek(self):
        m = Memory(size=10)
        m.poke(3, Quint.HIGH_UP)
        self.assertEqual(m.peek(3), Quint.HIGH_UP)
        self.assertEqual(m.peek(2), Quint.ZERO)
        self.assertEqual(m.peek(4), Quint.ZERO)

    def test_quint_number_address(self):
        m = Memory(size=10)
        addr = QuintNumber.from_int(5)
        m.poke(addr, Quint.LOW_DOWN)
        self.assertEqual(m.peek(addr), Quint.LOW_DOWN)
        self.assertEqual(m.peek(5), Quint.LOW_DOWN)

    def test_address_out_of_range(self):
        m = Memory(size=10)
        with self.assertRaises(IndexError):
            m.peek(10)
        with self.assertRaises(IndexError):
            m.poke(-1, Quint.ZERO)

    def test_poke_rejects_non_quint(self):
        m = Memory(size=10)
        with self.assertRaises(TypeError):
            m.poke(0, 3)


class TestRegisterFile(unittest.TestCase):
    def test_initial_zeros(self):
        rf = RegisterFile(["A", "B"])
        self.assertEqual(rf.read("A"), Quint.ZERO)
        self.assertEqual(rf.read("B"), Quint.ZERO)

    def test_write_and_read(self):
        rf = RegisterFile(["A", "B"])
        rf.write("A", Quint.HIGH_UP)
        self.assertEqual(rf.read("A"), Quint.HIGH_UP)
        self.assertEqual(rf.read("B"), Quint.ZERO)

    def test_unknown_register(self):
        rf = RegisterFile(["A"])
        with self.assertRaises(KeyError):
            rf.read("Z")
        with self.assertRaises(KeyError):
            rf.write("Z", Quint.ZERO)


if __name__ == "__main__":
    unittest.main()