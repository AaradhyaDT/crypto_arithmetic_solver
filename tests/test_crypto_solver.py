import pytest
from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized


def numeric_value(word: str, mapping: dict) -> int:
    return int(''.join(str(mapping[c]) for c in word))


def test_send_more_money():
    sol = solve_cryptarithmetic_optimized("SEND", "MORE", "MONEY")
    assert sol is not None
    assert numeric_value("SEND", sol) + numeric_value("MORE", sol) == numeric_value("MONEY", sol)


def test_return_all():
    sols = solve_cryptarithmetic_optimized("SEND", "MORE", "MONEY", return_all=True, max_solutions=5)
    assert isinstance(sols, list)
    assert len(sols) >= 1


def test_invalid_length():
    # impossible result length
    sol = solve_cryptarithmetic_optimized("A", "B", "CDE")
    assert sol is None
