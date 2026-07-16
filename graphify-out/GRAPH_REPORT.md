# Graph Report - AI  (2026-07-16)

## Corpus Check
- 21 files · ~6,770 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 76 nodes · 95 edges · 13 communities (9 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `71b2cb74`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `solve_cryptarithmetic_optimized()` - 17 edges
2. `Project layout` - 16 edges
3. `Puzzles Metrics Report` - 9 edges
4. `main()` - 5 edges
5. `solve()` - 4 edges
6. `cmd_solve()` - 3 edges
7. `_derive_solution_steps()` - 3 edges
8. `_derive_leading_bound()` - 3 edges
9. `Puzzle` - 3 edges
10. `test_send_more_money()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `run()` --calls--> `solve_cryptarithmetic_optimized()`  [INFERRED]
  tools/check_puzzles.py → src/crypto_arithmetic_solver.py
- `cmd_solve()` --calls--> `solve_cryptarithmetic_optimized()`  [EXTRACTED]
  cli.py → src/crypto_arithmetic_solver.py
- `test_invalid_length()` --calls--> `solve_cryptarithmetic_optimized()`  [EXTRACTED]
  tests/run_unit_tests.py → src/crypto_arithmetic_solver.py
- `test_return_all()` --calls--> `solve_cryptarithmetic_optimized()`  [EXTRACTED]
  tests/run_unit_tests.py → src/crypto_arithmetic_solver.py
- `test_invalid_length()` --calls--> `solve_cryptarithmetic_optimized()`  [EXTRACTED]
  tests/test_crypto_solver.py → src/crypto_arithmetic_solver.py

## Import Cycles
- None detected.

## Communities (13 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.20
Nodes (6): Crypto Arithmetic Solver Documentation, _derive_leading_bound(), _derive_solution_steps(), Compute the algebraic upper bound on the leading-column addend digit(s),     de, Replay the accepted assignment column-by-column (right-to-left) to build a, Convenience script: run puzzle checks, write JSON and readable report.

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (10): Column-wise cryptarithmetic solver with production safety features.      Args:, solve_cryptarithmetic_optimized(), numeric_value(), test_invalid_length(), test_return_all(), test_send_more_money(), numeric_value(), test_invalid_length() (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.40
Nodes (5): BaseModel, solve_cryptarithmetic_optimized, Puzzle, Solve puzzle. If `metrics=true` is provided as a query parameter, return metrics, solve()

### Community 3 - "Community 3"
Cohesion: 0.60
Nodes (5): cmd_export(), cmd_report(), cmd_solve(), cmd_test(), main()

### Community 4 - "Community 4"
Cohesion: 0.67
Nodes (3): Path, fmt_mapping(), main()

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (16): Algorithm (high level), Complexity, Contribution, Crypto Arithmetic solver.py, Deployment & FastAPI, Examples (from the test harness), File, Key files and locations (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (8): BASE+BALL=GAMES, CROSS+ROADS=DANGER, LETS+WAVE=LATER, LOGIC+LOGIC=PROLOG, Puzzles Metrics Report, SWIM+WEAR=RELAX, TWO+TWO=FOUR, WRONG+WRONG=RIGHT

## Knowledge Gaps
- **25 isolated node(s):** `Path`, `Crypto Arithmetic solver.py`, `Overview`, `Purpose`, `Algorithm (high level)` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Project layout` connect `Community 10` to `Community 0`?**
  _High betweenness centrality (0.292) - this node is a cross-community bridge._
- **Why does `solve_cryptarithmetic_optimized()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.271) - this node is a cross-community bridge._
- **Why does `Puzzles Metrics Report` connect `Community 11` to `Community 0`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `solve_cryptarithmetic_optimized()` (e.g. with `solve()` and `run()`) actually correct?**
  _`solve_cryptarithmetic_optimized()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Package marker for src.`, `Replay the accepted assignment column-by-column (right-to-left) to build a`, `Compute the algebraic upper bound on the leading-column addend digit(s),     de` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 10` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._