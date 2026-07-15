import sys
from pathlib import Path
# Ensure project root is on sys.path so `src` package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized


def numeric_value(word: str, mapping: dict) -> int:
    return int(''.join(str(mapping[c]) for c in word))


def test_send_more_money():
    sol: dict = solve_cryptarithmetic_optimized("SEND", "MORE", "MONEY")  # type: ignore[assignment]
    assert sol is not None
    assert numeric_value("SEND", sol) + numeric_value("MORE", sol) == numeric_value("MONEY", sol)


def test_return_all():
    sols = solve_cryptarithmetic_optimized("SEND", "MORE", "MONEY", return_all=True, max_solutions=5)
    assert isinstance(sols, list)
    assert len(sols) >= 1


def test_invalid_length():
    sol: dict = solve_cryptarithmetic_optimized("A", "B", "CDE")  # type: ignore[assignment]
    assert sol is None


if __name__ == '__main__':
    tests = [test_send_more_money, test_return_all, test_invalid_length]
    for t in tests:
        try:
            t()
            print(f"{t.__name__}: PASS")
        except AssertionError as e:
            print(f"{t.__name__}: FAIL ->", e)
            raise
