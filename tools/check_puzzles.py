import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crypto_arithmetic_solver import solve_cryptarithmetic_optimized

puzzles = [
    ("WRONG", "WRONG", "RIGHT"),
    ("BASE", "BALL", "GAMES"),
    ("TWO", "TWO", "FOUR"),
    ("SWIM", "WEAR", "RELAX"),
    ("LOGIC", "LOGIC", "PROLOG"),
    ("LETS", "WAVE", "LATER"),
    ("CROSS", "ROADS", "DANGER"),
]


def check_solution(w1, w2, res, mapping):
    if mapping is None:
        return False, "No solution"
    # Leading letters
    for w in (w1, w2, res):
        if len(w) > 1 and mapping[w[0]] == 0:
            return False, f"Leading zero for {w[0]} in {w}"

    # Unique digits
    vals = list(mapping.values())
    if len(vals) != len(set(vals)):
        return False, "Duplicate digits assigned"

    # Numeric check
    n1 = int(''.join(str(mapping[c]) for c in w1))
    n2 = int(''.join(str(mapping[c]) for c in w2))
    nr = int(''.join(str(mapping[c]) for c in res))
    if n1 + n2 != nr:
        return False, f"Arithmetic mismatch: {n1} + {n2} != {nr}"

    return True, f"OK: {n1} + {n2} = {nr}"


def run():
    for w1, w2, res in puzzles:
        sols, metrics = solve_cryptarithmetic_optimized(w1, w2, res, return_all=True, timeout=2, collect_metrics=True)
        if sols:
            # validate first solution
            valid, msg = check_solution(w1, w2, res, sols[0])
            print(f"{w1} + {w2} = {res}: FOUND -> {msg}")
            print("  solutions_found:", len(sols))
            print("  metrics:", metrics)
        else:
            print(f"{w1} + {w2} = {res}: NO solution within limits")


if __name__ == '__main__':
    run()
