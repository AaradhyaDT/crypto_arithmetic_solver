#!/usr/bin/env python
"""Simple CLI wrapper for common project tasks.

Commands:
  solve    Solve a single puzzle
  export   Generate JSON metrics for sample puzzles
  report   Generate Markdown report from JSON
  test     Run lightweight unit tests
"""
import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
TOOLS = ROOT / "tools"

sys.path.insert(0, str(ROOT))


def cmd_solve(args):
    from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized

    if args.metrics_json:
        sols, metrics = solve_cryptarithmetic_optimized(args.word1, args.word2, args.result, return_all=args.all, timeout=args.timeout, collect_metrics=True)  # type: ignore[misc]
        import json
        out = {"solutions": sols, "metrics": metrics}
        with open(args.metrics_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(args.metrics_json)
    else:
        sols = solve_cryptarithmetic_optimized(args.word1, args.word2, args.result, return_all=args.all, timeout=args.timeout)
        print(sols)


def cmd_export(_):
    subprocess.run([sys.executable, str(TOOLS / "puzzles_metrics_json.py")], check=True)


def cmd_report(argv):
    cmd = [sys.executable, str(TOOLS / "generate_readable_report.py")]
    if argv and argv[0].isdigit():
        cmd.append(argv[0])
    subprocess.run(cmd, check=True)


def cmd_test(_):
    subprocess.run([sys.executable, str(ROOT / "tests" / "run_unit_tests.py")], check=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="cli")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("solve")
    p.add_argument("word1")
    p.add_argument("word2")
    p.add_argument("result")
    p.add_argument("--all", action="store_true")
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--metrics-json", default=None)

    sub.add_parser("export")

    p2 = sub.add_parser("report")
    p2.add_argument("max_display", nargs="?", default=None)

    sub.add_parser("test")

    args, rest = parser.parse_known_args()
    if args.cmd == "solve":
        cmd_solve(args)
    elif args.cmd == "export":
        cmd_export(args)
    elif args.cmd == "report":
        cmd_report(rest)
    elif args.cmd == "test":
        cmd_test(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
