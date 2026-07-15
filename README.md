# Project layout

- `src/` — main solver `crypto_arithmetic_solver.py` and `fastapi_app.py`
- `tools/` — helper scripts: `puzzles_metrics_json.py`, `generate_readable_report.py`, `check_puzzles.py`, `check_and_export.py`
- `tests/` — simple test runner: `run_unit_tests.py`
- `reports/` — generated outputs: `puzzles_metrics.json`, `puzzles_metrics_report.md`
- `docs/` — human-readable docs

Quick commands

- Run the solver CLI and write metrics JSON:

```python src/crypto_arithmetic_solver.py SEND MORE MONEY --metrics-json reports/send_more_metrics.json --timeout 2
```

- Generate reports for the suite of puzzles (JSON + Markdown):

```python tools/check_and_export.py
```

- Run the PowerShell helper (interactive) to solve a puzzle and emit metrics JSON:

```powershell
pwsh .\solve_with_metrics.ps1 -Word1 SEND -Word2 MORE -Result MONEY -Timeout 2
```

The script prints the found mapping and metrics to the console and writes a report JSON to the `reports/` folder.

- Run tests (no pytest required):

```python tests/run_unit_tests.py
```

## Crypto Arithmetic solver.py

## Overview

This repository contains `crypto_arithmetic_solver.py` (import-ready name), a production-oriented cryptarithmetic solver implemented in Python. It uses a column-by-column (right-to-left) backtracking algorithm that prunes invalid branches immediately when a column's arithmetic fails, making it far more efficient than naive "generate-and-test" approaches.

## Purpose

- Solve alphametic puzzles of the form WORD1 + WORD2 = RESULT where each letter maps to a unique digit (0-9).
- Return a mapping of letters to digits for the first valid solution found.
- Provide a compact, thread-safe function suitable for embedding in services or agents.

## Algorithm (high level)

1. Normalize inputs to uppercase.
2. Early-exit checks:
   - Validate the `result` length is either max(len(word1), len(word2)) or +1.
   - Ensure there are no more than 10 unique letters (base-10 limitation).
3. Reverse each string to traverse columns from units to most-significant digit.
4. Identify leading letters (most-significant characters) that cannot be assigned zero.
5. Use a column-by-column DFS that assigns digits only as needed for the current column:
   - For addend rows, assign or skip letters (respecting used digits and leading-zero rules).
   - On the result row, compute the column sum + carry to obtain the required target digit.
   - If the target digit conflicts with assignments or used digits (or is illegal 0 for a leading letter), prune the branch immediately.
6. Propagate carry to the next column. If all columns pass and final carry is zero, a solution is found.

This mirrors the way a human solves alphametics and vastly reduces the explored state space.

## Public API

- `solve_cryptarithmetic_optimized(word1: str, word2: str, result: str) -> Optional[Dict[str, int]]`
  - Returns a dict mapping letters to digits for the first solution found, or `None` if no solution exists.
  - Side-effects: none outside its scope (`assigned` and `used_digits` live inside the function).

## Usage

Run the file as a script to execute a small built-in CLI test harness (arguments: `word1 word2 result`). Example:

```bash
python "d:\AaradhyaDT\AI\crypto_arithmetic_solver.py" SEND MORE MONEY
```

Or import the function into other modules:

```python
from crypto_arithmetic_solver import solve_cryptarithmetic_optimized
solution = solve_cryptarithmetic_optimized("SEND", "MORE", "MONEY")
```

## Complexity

- Worst-case search remains exponential in the number of unique letters, but the column-wise pruning reduces branches drastically in practice. Typical 5–6 letter puzzles solve in milliseconds.
- The algorithm avoids the factorial blow-up of naive full-assignment generate-and-test by validating arithmetic as soon as possible.

## Thread-Safety & Production Notes

- `assigned` and `used_digits` are local to the function, so concurrent calls from multiple threads/processes are safe provided the caller does not mutate the returned mapping.
- For API use, add a short timeout or candidate-limit to avoid pathological cases.

## Known Fixes & Current Behavior

- Fixed an earlier bug where leading characters were detected incorrectly: the solver now treats the first/most-significant character of each multi-letter word as the leading character (cannot be zero).

## Examples (from the test harness)

- `SEND + MORE = MONEY` → returns mapping and verifies the numeric sum.
- `WRONG + WRONG = RIGHT` → returns mapping for repeated addend case.
- `BASE + BALL = GAMES` → returns mapping for different lengths.

Example run output (sample):

```Solution for SEND + MORE = MONEY:
{'D': 7, 'E': 5, 'Y': 2, 'N': 6, 'R': 8, 'O': 0, 'S': 9, 'M': 1}
9567 + 1085 = 10652
```

## Limitations & Future Enhancements

- Returns the first solution found; to enumerate all solutions, modify the DFS to yield instead of short-circuiting on `True`.
- Heuristics such as Most-Restricted-Variable (MRV) or ordering digits by likelihood (e.g., prefer digits that keep carries consistent) can further speed up hard puzzles.
- Add a `timeout` parameter or limit on recursive calls to prevent long-running requests in a service environment.
- Consider renaming the file to `crypto_arithmetic_solver.py` for import convenience.

## Contribution

If you want me to:

- Add a `--all` flag to return all solutions,
- Add `pytest` tests and CI config,
- Expose a small Flask/FastAPI wrapper for remote solving,

say which and I'll implement it.

## File

- `[crypto_arithmetic_solver.py](crypto_arithmetic_solver.py)`

---

Generated by a helper script to document the solver and recommended next steps.
