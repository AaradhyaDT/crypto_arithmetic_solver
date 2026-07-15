import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "puzzles_metrics.json"
OUTPUT = ROOT / "reports" / "puzzles_metrics_report.md"
MAX_DISPLAY = 5


def fmt_mapping(m):
    return ", ".join(f"{k}:{v}" for k, v in sorted(m.items()))


def main(input_path: Path = INPUT, output_path: Path = OUTPUT, max_display: int = MAX_DISPLAY):
    if not input_path.exists():
        print(f"Input not found: {input_path}")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))

    lines = ["# Puzzles Metrics Report", ""]

    for key, info in data.items():
        lines.append(f"## {key}")
        metrics = info.get("metrics", {})
        lines.append("")
        lines.append(f"- Solutions found: **{info.get('solutions_count', 0)}**")
        lines.append(f"- Elapsed (s): **{metrics.get('elapsed_seconds', 0):.6f}**")
        lines.append(f"- Recursive calls: **{metrics.get('recursive_calls', 0)}**")
        lines.append(f"- Assignments: **{metrics.get('assignments', 0)}**")
        lines.append(f"- Backtracks: **{metrics.get('backtracks', 0)}**")
        lines.append("")

        sols = info.get("solutions", [])
        if not sols:
            lines.append("No solutions recorded.")
            lines.append("")
            continue

        display_n = min(len(sols), max_display)
        lines.append(f"Showing first {display_n} solution(s):")
        lines.append("")
        for i, sol in enumerate(sols[:display_n], start=1):
            # numeric representation if possible
            try:
                left, right = key.split("=")
                w1, w2 = left.split("+")
                mapping = sol
                n1 = int("".join(str(mapping[c]) for c in w1))
                n2 = int("".join(str(mapping[c]) for c in w2))
                nr = int("".join(str(mapping[c]) for c in right))
                lines.append(f"{i}. {n1} + {n2} = {nr}    —    {fmt_mapping(mapping)}")
            except Exception:
                lines.append(f"{i}. {fmt_mapping(sol)}")

        if len(sols) > display_n:
            lines.append("")
            lines.append(f"...and {len(sols)-display_n} more solutions. To show all, re-run the exporter with a higher max_display.")

        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == '__main__':
    max_display = MAX_DISPLAY
    if len(sys.argv) > 1:
        try:
            max_display = int(sys.argv[1])
        except Exception:
            pass
    main(max_display=max_display)
