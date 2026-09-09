# Expand Question Domain for Cryptarithmetic Solver

## Overview
Currently, the codebase is constrained to 2-addend addition puzzles of the exact form `WORD1 + WORD2 = RESULT` (e.g., `SEND + MORE = MONEY`, `BASE + BALL = GAMES`).
"Expand question domain" can address two complementary dimensions:
1. **Algorithmic / Functional Domain**: Expanding solver and checker capabilities beyond the 2-addend restriction:
   - **Arbitrary $N$-addends** ($N \ge 2$, e.g., `FORTY + TEN + TEN = SIXTY`, `APPLE + LEMON + BANANA = ORANGE`, `A + B + C + D = E`).
   - **General Puzzle Expression Parsing** (e.g., `"SEND + MORE = MONEY"`, `"CROSS + ROADS = DANGER"`, `"COFFEE + TEA + CAKE = ENERGY"` passed as a single string).
   - **Subtraction support** ($A - B = C$, natively or transformed via arithmetic equivalence $B + C = A$).
2. **Benchmark / Problem Catalog Domain**: Expanding the suite of curated test puzzles in `tools/check_puzzles.py`, `tools/puzzles_metrics_json.py`, and test suites with a richer variety of classic, multi-word, varying-difficulty, and edge-case puzzles.

---

## User Review Required

> [!IMPORTANT]
> Please review and confirm the scope of the domain expansion you would like:
> - **Scope A (Recommended - Comprehensive)**:
>   1. **Generalized $N$-addend Solver**: Support arbitrary list of addends ($W_1 + W_2 + \dots + W_k = R$) in `solve_cryptarithmetic`, `check_solution`, `parse_answer`, while keeping backwards-compatible signatures for `solve_cryptarithmetic_optimized(word1, word2, result)`.
>   2. **Equation String Parser**: Allow inputs like `"FORTY + TEN + TEN = SIXTY"` directly in CLI, PowerShell helpers, API, and Python functions.
>   3. **Expanded Puzzle Catalog**: Expand the standard puzzle benchmark suite from 7 two-word puzzles to a categorized library of 20+ classic puzzles across 2-addend, multi-addend ($3+$ words), single-digit, and multi-solution puzzles.
> - **Scope B (Dataset / Benchmark Expansion Only)**:
>   Keep the solver strictly 2-addends, but add 20+ diverse 2-addend puzzles with varying difficulty, unique vs multi-solution, and metric benchmarks.
> - **Scope C (Include Subtraction / Multiplication)**:
>   In addition to $N$-addends, support subtraction ($A - B = C$) and multiplication ($A \times B = C$).

---

## Proposed Changes

### Core Solver & Domain Engine

#### [MODIFY] [crypto_arithmetic_solver.py](file:///f:/AaradhyaDT/AI/src/crypto_arithmetic_solver.py)
- **Generalize search algorithm**:
  - Replace the fixed 3-row loop (`words = [w1, w2, res]`) with a generalized $K$-addend column-by-column DFS (`words = [a1, a2, ..., aK, res]`).
  - At each column $c$, traverse addends $0 \dots K-1$; at result row $K$, compute $\text{sum} = \text{carry} + \sum_{i=0}^{K-1} \text{addend}_i[c]$. Target digit is $\text{sum} \pmod{10}$, next carry is $\text{sum} // 10$.
  - Maintain leading bound logic generalized for $K$ addends.
  - Update `_derive_solution_steps` to format steps for arbitrary $K$ addends (e.g. `FORTY(29786) + TEN(850) + TEN(850) = SIXTY(31486)`).
- **Public API additions**:
  - Add `solve_cryptarithmetic(addends: Union[List[str], str], result: Optional[str] = None, ...)` that accepts either a list of words + result or an equation string (e.g., `"SEND + MORE = MONEY"`).
  - Retain `solve_cryptarithmetic_optimized(word1, word2, result, ...)` with identical signatures for 100% backward compatibility.
- **Generalize `check_solution` and `parse_answer`**:
  - Support list of words `addends: Sequence[str], result: str` or single equation string `"W1 + W2 + ... = RES"`.
  - In `parse_answer`, support $K+1$ space-separated numbers matching $K$ addends and result.

---

### CLI & PowerShell Integration

#### [MODIFY] [cli.py](file:///f:/AaradhyaDT/AI/cli.py)
- Allow `cli.py solve` and `cli.py check` to accept either:
  - An equation string as a single argument: `python cli.py solve "FORTY + TEN + TEN = SIXTY"`
  - Multiple addends followed by result: `python cli.py solve FORTY TEN TEN SIXTY` (or `--addends FORTY TEN TEN --result SIXTY`)
  - Legacy 3-argument syntax `python cli.py solve SEND MORE MONEY`.

#### [MODIFY] [check_solution.ps1](file:///f:/AaradhyaDT/AI/check_solution.ps1) & [solve_with_metrics.ps1](file:///f:/AaradhyaDT/AI/solve_with_metrics.ps1)
- Support passing an equation string (e.g. `.\solve_with_metrics.ps1 "FORTY + TEN + TEN = SIXTY"`) or multiple addends.

---

### API & Benchmarks

#### [MODIFY] [fastapi_app.py](file:///f:/AaradhyaDT/AI/src/fastapi_app.py)
- Extend `Puzzle` and `CheckPuzzle` models to accept `addends: Optional[List[str]] = None` and `equation: Optional[str] = None` while preserving `word1` and `word2` fields.

#### [MODIFY] [check_puzzles.py](file:///f:/AaradhyaDT/AI/tools/check_puzzles.py) & [puzzles_metrics_json.py](file:///f:/AaradhyaDT/AI/tools/puzzles_metrics_json.py)
- Expand the puzzle collection with a structured catalog:
  - Classic 2-addend (e.g. `SEND+MORE=MONEY`, `BASE+BALL=GAMES`, `CROSS+ROADS=DANGER`, `DONALD+GERALD=ROBERT`, `SATURN+URANUS=PLANETS`).
  - 3-addend & multi-addend (e.g. `FORTY+TEN+TEN=SIXTY`, `APPLE+LEMON+BANANA=ORANGE`, `EARTH+AIR+FIRE+WATER=NATURE`, `OH+NO+SEE=SOON`).
  - Varying difficulty (from 4 unique letters to maximum 10 unique letters).

---

### Testing

#### [MODIFY] [test_crypto_solver.py](file:///f:/AaradhyaDT/AI/tests/test_crypto_solver.py)
- Add unit tests for:
  - Multi-addend solving (`FORTY + TEN + TEN = SIXTY`).
  - Equation string parsing (`"SEND + MORE = MONEY"`).
  - Multi-addend solution validation in `check_solution` and `parse_answer`.
  - Regression tests ensuring all existing 2-addend tests pass unchanged.

---

## Verification Plan

### Automated Tests
- Run `python tests/run_unit_tests.py` to ensure all existing and new unit tests pass.
- Run `python tools/check_puzzles.py` to verify the expanded puzzle catalog.
- Run `python tools/check_and_export.py` to re-generate `reports/puzzles_metrics.json` and `reports/puzzles_metrics_report.md`.

### Manual Verification
- Test PowerShell script:
  `pwsh .\check_solution.ps1 "FORTY + TEN + TEN = SIXTY" "29786 850 850 31486"`
- Test CLI:
  `python cli.py solve "FORTY + TEN + TEN = SIXTY"`
  `python cli.py check SEND MORE MONEY "9567 1085 10652"`
