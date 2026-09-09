import sys
from pathlib import Path
# Ensure project root is on sys.path so `src` package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.crypto_arithmetic_solver import (
    solve_cryptarithmetic_optimized,
    check_solution,
    parse_mapping,
)


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


def test_check_solution_valid():
    mapping = {"S": 9, "E": 5, "N": 6, "D": 7, "M": 1, "O": 0, "R": 8, "Y": 2}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is True
    assert "OK: 9567 + 1085 = 10652" in msg


def test_check_solution_arithmetic_mismatch():
    mapping = {"S": 9, "E": 5, "N": 6, "D": 7, "M": 1, "O": 0, "R": 8, "Y": 3}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is False
    assert "Arithmetic mismatch" in msg


def test_check_solution_leading_zero():
    mapping = {"S": 0, "E": 5, "N": 6, "D": 7, "M": 1, "O": 9, "R": 8, "Y": 2}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is False
    assert "Leading zero for 'S'" in msg


def test_check_solution_duplicate_digits():
    mapping = {"S": 9, "E": 5, "N": 6, "D": 7, "M": 9, "O": 0, "R": 8, "Y": 2}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is False
    assert "Duplicate digits" in msg


def test_check_solution_missing_char():
    mapping = {"S": 9, "E": 5, "N": 6, "D": 7}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is False
    assert "Missing mapping for character(s)" in msg


def test_check_solution_invalid_digit():
    mapping = {"S": 9, "E": 5, "N": 6, "D": 7, "M": 1, "O": 0, "R": 8, "Y": 15}
    valid, msg = check_solution("SEND", "MORE", "MONEY", mapping)
    assert valid is False
    assert "out of bounds" in msg


def test_parse_mapping_formats():
    parsed_pairs = parse_mapping("S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2")
    assert parsed_pairs["S"] == 9 and parsed_pairs["Y"] == 2
    parsed_json = parse_mapping("{'S': 9, 'E': 5}")
    assert parsed_json["S"] == 9 and parsed_json["E"] == 5


if __name__ == '__main__':
    tests = [
        test_send_more_money,
        test_return_all,
        test_invalid_length,
        test_check_solution_valid,
        test_check_solution_arithmetic_mismatch,
        test_check_solution_leading_zero,
        test_check_solution_duplicate_digits,
        test_check_solution_missing_char,
        test_check_solution_invalid_digit,
        test_parse_mapping_formats,
    ]
    for t in tests:
        try:
            t()
            print(f"{t.__name__}: PASS")
        except AssertionError as e:
            print(f"{t.__name__}: FAIL ->", e)
            raise

