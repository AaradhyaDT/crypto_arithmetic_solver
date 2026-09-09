#!/usr/bin/env python
"""Simple CLI wrapper for common project tasks.

Commands:
  solve    Solve a single puzzle
  check    Check if a candidate mapping solves a puzzle
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

    w1 = args.word1 or input("Enter first addend (word1): ").strip()
    w2 = args.word2 or input("Enter second addend (word2): ").strip()
    res = args.result or input("Enter result word: ").strip()

    if args.metrics_json:
        sols, metrics = solve_cryptarithmetic_optimized(w1, w2, res, return_all=args.all, timeout=args.timeout, collect_metrics=True)  # type: ignore[misc]
        import json
        out = {"solutions": sols, "metrics": metrics}
        with open(args.metrics_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(args.metrics_json)
    else:
        sols = solve_cryptarithmetic_optimized(w1, w2, res, return_all=args.all, timeout=args.timeout)
        print(sols)


def cmd_check(args):
    from src.crypto_arithmetic_solver import check_solution, parse_answer

    w1 = args.word1 or input("Enter first addend (word1): ").strip()
    w2 = args.word2 or input("Enter second addend (word2): ").strip()
    res = args.result or input("Enter result word: ").strip()

    raw_answer = None
    if args.answer:
        raw_answer = " ".join(args.answer)
    elif args.mapping:
        raw_answer = args.mapping
    elif args.mapping_json:
        raw_answer = args.mapping_json
    else:
        raw_answer = input(f"Enter answer for {w1} + {w2} = {res} (mapping, numbers, or JSON file): ").strip()

    try:
        mappings = parse_answer(w1, w2, res, raw_answer)
    except Exception as e:
        print(f"Error reading/parsing answer: {e}", file=sys.stderr)
        sys.exit(1)

    if not mappings:
        print("No solutions found to check.", file=sys.stderr)
        sys.exit(1)

    if len(mappings) == 1:
        valid, msg = check_solution(w1, w2, res, mappings[0])
        print(f"Valid: {valid}")
        print(msg)
        sys.exit(0 if valid else 1)
    else:
        print(f"Checking {len(mappings)} solution(s) for {w1} + {w2} = {res}:")
        all_valid = True
        valid_count = 0
        for idx, m in enumerate(mappings, start=1):
            valid, msg = check_solution(w1, w2, res, m)
            if valid:
                valid_count += 1
            else:
                all_valid = False
            print(f"  [{idx}/{len(mappings)}] Valid: {valid} -> {msg}")
        print(f"\nResult: {valid_count} of {len(mappings)} solution(s) valid.")
        sys.exit(0 if all_valid else 1)


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

    p = sub.add_parser("solve", help="Solve a puzzle")
    p.add_argument("word1", nargs="?", default=None, help="First addend")
    p.add_argument("word2", nargs="?", default=None, help="Second addend")
    p.add_argument("result", nargs="?", default=None, help="Result word")
    p.add_argument("--all", action="store_true")
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--metrics-json", default=None)

    p_check = sub.add_parser("check", help="Check a candidate solution for a puzzle")
    p_check.add_argument("word1", nargs="?", default=None, help="First addend")
    p_check.add_argument("word2", nargs="?", default=None, help="Second addend")
    p_check.add_argument("result", nargs="?", default=None, help="Result word")
    p_check.add_argument("answer", nargs="*", default=None, help="Answer as numbers (7483 7455 14938), mapping (A=4,B=7...), or JSON file")
    p_check.add_argument("--mapping", default=None, help="Mapping as JSON or key=val pairs")
    p_check.add_argument("--mapping-json", default=None, help="Path to JSON file containing mapping(s)")

    sub.add_parser("export")

    p2 = sub.add_parser("report")
    p2.add_argument("max_display", nargs="?", default=None)

    sub.add_parser("test")

    args, rest = parser.parse_known_args()
    if args.cmd == "solve":
        cmd_solve(args)
    elif args.cmd == "check":
        cmd_check(args)
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

