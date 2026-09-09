import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crypto_arithmetic_solver import solve_cryptarithmetic_optimized, check_solution

puzzles = [
    ("WRONG", "WRONG", "RIGHT"),
    ("BASE", "BALL", "GAMES"),
    ("TWO", "TWO", "FOUR"),
    ("SWIM", "WEAR", "RELAX"),
    ("LOGIC", "LOGIC", "PROLOG"),
    ("LETS", "WAVE", "LATER"),
    ("CROSS", "ROADS", "DANGER"),
]


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
