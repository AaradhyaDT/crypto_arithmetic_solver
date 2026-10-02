#!/usr/bin/env python3
"""
verify.py — Deterministic verification suite for crypto_arithmetic_solver

Checks:
  1. Python syntax across codebase
  2. Full test suite execution (pytest)
  3. Commit SHA integrity: Prohibits placeholder tokens (relXX, upgXX, xtoolXX, dummy, todo)
     and validates all commit references are authentic 7-40 hex SHAs.

Run:
  python scripts/verify.py
  python scripts/verify.py --verbose

Exit codes: 0 = clean, 1 = errors found
"""
import ast
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

errors = []
passes = []

VERBOSE = "--verbose" in sys.argv


def ok(msg):
    passes.append(msg)
    if VERBOSE:
        print(f"  [PASS] {msg}")


def err(msg):
    errors.append(msg)
    print(f"  [FAIL] {msg}")


def check_python_syntax():
    print("\n[1/3] Python AST syntax check")
    py_files = []
    for root_dir, _, files in os.walk("."):
        if any(d in root_dir for d in [".git", ".venv", "__pycache__", "graphify-out"]):
            continue
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root_dir, file))

    syntax_errors = 0
    for f in py_files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                ast.parse(fh.read(), filename=f)
            ok(f"{f} AST parsed successfully")
        except SyntaxError as e:
            err(f"{f}: syntax error line {e.lineno}: {e.msg}")
            syntax_errors += 1

    if syntax_errors == 0:
        ok(f"all {len(py_files)} python files valid")


def check_tests():
    print("\n[2/3] Pytest test suite")
    res = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    if res.returncode == 0:
        ok("pytest suite passed (100% tests green)")
    else:
        err(f"pytest failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}")


def check_commit_sha_integrity():
    print("\n[3/3] Commit SHA & placeholder integrity")
    placeholder_pattern = re.compile(r"\b(rel\d+|upg\d+|xtool\d+|dummy|todo)\b", re.IGNORECASE)
    commit_url_pattern = re.compile(r"github\.com/[^/]+/[^/]+/commit/([a-zA-Z0-9_\-]+)")
    sha_prop_pattern = re.compile(r"""sha:\s*['"]([^'"]+)['"]""")
    hex_sha_pattern = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)

    scanned_extensions = {".md", ".py", ".json", ".ps1", ".txt"}
    bad_shas = []

    for root_dir, _, files in os.walk("."):
        if any(d in root_dir for d in [".git", ".venv", "__pycache__", "graphify-out"]):
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in scanned_extensions:
                file_path = os.path.join(root_dir, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                except Exception:
                    continue

                for m in commit_url_pattern.finditer(content):
                    sha = m.group(1)
                    if placeholder_pattern.match(sha) or not hex_sha_pattern.match(sha):
                        bad_shas.append(f"{file_path}: invalid commit URL SHA '{sha}'")

                for m in sha_prop_pattern.finditer(content):
                    sha = m.group(1)
                    if placeholder_pattern.match(sha) or not hex_sha_pattern.match(sha):
                        bad_shas.append(f"{file_path}: invalid sha property '{sha}'")

    if bad_shas:
        for b in bad_shas:
            err(b)
    else:
        ok("all commit SHAs are authentic 7-40 hex format (0 placeholders found)")


def main():
    print(f"Running deterministic verification in {ROOT}")
    check_python_syntax()
    check_tests()
    check_commit_sha_integrity()

    print(f"\n{'='*50}")
    print(f"Passed: {len(passes)}   Errors: {len(errors)}")
    if errors:
        print("\nFAILED — fix the above before proceeding.")
        sys.exit(1)
    print("\nALL CHECKS PASSED DETERMINISTICALLY.")
    sys.exit(0)


if __name__ == "__main__":
    main()
