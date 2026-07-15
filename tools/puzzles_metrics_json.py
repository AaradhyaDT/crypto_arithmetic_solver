import json
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

output = {}
for w1, w2, res in puzzles:
    sols, metrics = solve_cryptarithmetic_optimized(w1, w2, res, return_all=True, timeout=2, collect_metrics=True)
    output[f"{w1}+{w2}={res}"] = {
        "solutions_count": len(sols),
        "solutions": sols,
        "metrics": metrics,
    }

path = Path(__file__).resolve().parents[1] / "reports" / "puzzles_metrics.json"
path.parent.mkdir(parents=True, exist_ok=True)
with open(path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(path)
