from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized, check_solution, parse_mapping


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


def test_check_multiple_solutions():
    from src.crypto_arithmetic_solver import check_solutions
    sols = solve_cryptarithmetic_optimized("TWO", "TWO", "FOUR", return_all=True)
    assert isinstance(sols, list) and len(sols) == 7
    results = check_solutions("TWO", "TWO", "FOUR", sols)
    assert len(results) == 7
    for valid, msg in results:
        assert valid is True
        assert "OK:" in msg


def test_load_mappings_from_json():
    from src.crypto_arithmetic_solver import load_mappings_from_json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "reports" / "two_four_metrics.json"
    if path.exists():
        mappings = load_mappings_from_json(path)
        assert len(mappings) == 7


def test_parse_answer_numbers():
    from src.crypto_arithmetic_solver import parse_answer
    mappings = parse_answer("BASE", "BALL", "GAMES", "7483 7455 14938")
    assert len(mappings) == 1
    assert mappings[0]["B"] == 7 and mappings[0]["A"] == 4 and mappings[0]["S"] == 8
    assert mappings[0]["E"] == 3 and mappings[0]["L"] == 5 and mappings[0]["G"] == 1
    assert mappings[0]["M"] == 9



