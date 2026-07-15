from typing import Dict, Optional, List, Union, Tuple, overload
try:
    from typing import Literal
except Exception:
    from typing_extensions import Literal
import time


def _derive_solution_steps(
    word1: str, word2: str, result: str, solution: Dict[str, int]
) -> List[Dict[str, Union[int, str]]]:
    """
    Replay the accepted assignment column-by-column (right-to-left) to build a
    human-readable derivation for the winning solution. Backtracked/rejected
    attempts are intentionally excluded — only the final accepted path is shown.
    """
    w1, w2, res = word1[::-1], word2[::-1], result[::-1]
    steps: List[Dict[str, Union[int, str]]] = []
    carry = 0

    for col in range(len(res)):
        terms: List[str] = []
        col_sum = 0

        if col < len(w1):
            ch = w1[col]
            terms.append(f"{ch}({solution[ch]})")
            col_sum += solution[ch]
        if col < len(w2):
            ch = w2[col]
            terms.append(f"{ch}({solution[ch]})")
            col_sum += solution[ch]

        expr = " + ".join(terms) if terms else ""
        if carry:
            expr = f"{expr} + carry {carry}" if expr else f"carry {carry}"

        col_sum += carry
        out_digit = col_sum % 10
        next_carry = col_sum // 10
        out_char = res[col]

        equation = f"{expr} = {out_char}({out_digit})" if next_carry == 0 else (
            f"{expr} = {out_char}({out_digit}), carry {next_carry}"
        )

        steps.append({
            "column": col + 1,
            "equation": equation,
        })

        carry = next_carry

    return steps


@overload
def solve_cryptarithmetic_optimized(
    word1: str,
    word2: str,
    result: str,
    *,
    return_all: Literal[False] = ...,
    max_solutions: Optional[int] = ...,
    timeout: Optional[float] = ...,
    max_calls: Optional[int] = ...,
    collect_metrics: Literal[True],
) -> Tuple[Optional[Dict[str, int]], Dict[str, Union[int, float]]]:
    ...


@overload
def solve_cryptarithmetic_optimized(
    word1: str,
    word2: str,
    result: str,
    *,
    return_all: Literal[True],
    max_solutions: Optional[int] = ...,
    timeout: Optional[float] = ...,
    max_calls: Optional[int] = ...,
    collect_metrics: Literal[True],
) -> Tuple[List[Dict[str, int]], Dict[str, Union[int, float]]]:
    ...


@overload
def solve_cryptarithmetic_optimized(
    word1: str,
    word2: str,
    result: str,
    *,
    return_all: Literal[False] = ...,
    max_solutions: Optional[int] = ...,
    timeout: Optional[float] = ...,
    max_calls: Optional[int] = ...,
    collect_metrics: Literal[False] = ...,
) -> Optional[Dict[str, int]]:
    ...


@overload
def solve_cryptarithmetic_optimized(
    word1: str,
    word2: str,
    result: str,
    *,
    return_all: Literal[True],
    max_solutions: Optional[int] = ...,
    timeout: Optional[float] = ...,
    max_calls: Optional[int] = ...,
    collect_metrics: Literal[False] = ...,
) -> List[Dict[str, int]]:
    ...


def _derive_leading_bound(word1: str, word2: str, result: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Compute the algebraic upper bound on the leading-column addend digit(s),
    derivable purely from word structure before any search/assignment happens.

    Only applies when the leading (final, most-significant) column has both
    word1 and word2 contributing a digit there (i.e. result is the same length
    as the longer addend, not one digit longer). If result is one digit longer,
    the leading column is carry-only and this bound doesn't apply.
    """
    max_addend_len = max(len(word1), len(word2))
    if len(result) != max_addend_len:
        return None  # result has an extra leading digit; leading column is carry-only

    lead1 = word1[0] if len(word1) == max_addend_len else None
    lead2 = word2[0] if len(word2) == max_addend_len else None

    if lead1 is None or lead2 is None:
        return None  # shouldn't happen given the length check above, but guard anyway

    # Worst-case carry_in into the leading column is always 1 (max column sum is 9+9+1=19,
    # so carry out of any column never exceeds 1) -- so the bound must hold even if carry_in=1,
    # making it a fact that's true regardless of how the rest of the search resolves.
    max_carry_in = 1

    if lead1 == lead2:
        # Same letter on both addends: 2*X + carry_in <= 9
        bound = (9 - max_carry_in) // 2
        return {
            "column": max_addend_len,
            "note": (
                f"leading column: {lead1}+{lead1}(+carry) must be a single digit "
                f"(no column left to absorb a further carry), so 2*{lead1} + 1 <= 9 -> {lead1} <= {bound}"
            ),
        }
    else:
        # Different letters: can't collapse to a single-variable bound, but the
        # joint constraint is still a real, statable, upfront fact.
        return {
            "column": max_addend_len,
            "note": (
                f"leading column: {lead1}+{lead2}(+carry) must be a single digit "
                f"(no column left to absorb a further carry), so {lead1} + {lead2} + 1 <= 9"
            ),
        }


def solve_cryptarithmetic_optimized(
    word1: str,
    word2: str,
    result: str,
    return_all: bool = False,
    max_solutions: Optional[int] = None,
    timeout: Optional[float] = None,
    max_calls: Optional[int] = None,
    collect_metrics: bool = False,
) -> Union[
    Optional[Dict[str, int]],
    List[Dict[str, int]],
    Tuple[Optional[Dict[str, int]], Dict[str, Union[int, float]]],
    Tuple[List[Dict[str, int]], Dict[str, Union[int, float]]],
]:
    """
    Column-wise cryptarithmetic solver with production safety features.

    Args:
        word1, word2, result: puzzle strings (e.g. SEND, MORE, MONEY)
        return_all: if True, return a list of all solutions found (subject to limits).
        max_solutions: stop after this many solutions (only used when return_all=True).
        timeout: maximum time in seconds to search (None = unlimited).
        max_calls: maximum number of recursive calls allowed (None = unlimited).

    Returns:
        If return_all is False: first-found mapping or None.
        If return_all is True: list of mappings (possibly empty).
    """
    word1, word2, result = word1.upper(), word2.upper(), result.upper()

    # Early checks
    if len(result) < max(len(word1), len(word2)) or len(result) > max(len(word1), len(word2)) + 1:
        return [] if return_all else None

    unique_chars = list(dict.fromkeys(word1 + word2 + result))  # keep deterministic order
    if len(unique_chars) > 10:
        return [] if return_all else None

    words = [word1[::-1], word2[::-1], result[::-1]]
    leading_chars = {w[0] for w in [word1, word2, result] if len(w) > 1}

    assigned: Dict[str, int] = {}
    used_digits = set()
    solutions: List[Dict[str, int]] = []
    decision_trace: List[Dict[str, Union[str, int, List[int]]]] = []
    trace_snapshots: List[Dict[str, Union[int, List[Dict]]]] = []

    start_time = time.monotonic()
    calls = 0
    backtracks = 0
    assignments = 0

    def timed_out() -> bool:
        if timeout is None:
            return False
        return (time.monotonic() - start_time) >= timeout

    def solve(col: int, row: int, carry: int) -> bool:
        nonlocal calls
        nonlocal backtracks, assignments
        calls += 1
        if max_calls is not None and calls > max_calls:
            return False
        if timed_out():
            return False

        # All columns processed
        if col == len(words[2]):
            if carry == 0:
                # record solution
                sol = dict(assigned)
                solutions.append(sol)
                trace_snapshots.append({
                    "solution_index": len(solutions) - 1,
                    "calls_to_reach": calls,
                    "trace": list(decision_trace),
                })
                if not return_all:
                    return True
                if max_solutions is not None and len(solutions) >= max_solutions:
                    return True
            return False

        # Result row (row == 2)
        if row == 2:
            col_sum = carry
            depends_on: List[str] = []
            if col < len(words[0]):
                ch0 = words[0][col]
                if ch0 not in assigned:
                    return False
                col_sum += assigned[ch0]
                depends_on.append(f"{ch0}={assigned[ch0]}")
            if col < len(words[1]):
                ch1 = words[1][col]
                if ch1 not in assigned:
                    return False
                col_sum += assigned[ch1]
                depends_on.append(f"{ch1}={assigned[ch1]}")
            if carry:
                depends_on.append(f"carry {carry} (from column {col})")

            target_digit = col_sum % 10
            next_carry = col_sum // 10
            char = words[2][col]

            if char in assigned:
                if assigned[char] == target_digit:
                    return solve(col + 1, 0, next_carry)
                return False

            # If not assigned, try the target digit if available
            if target_digit in used_digits or (target_digit == 0 and char in leading_chars):
                return False

            assigned[char] = target_digit
            used_digits.add(target_digit)
            assignments += 1
            depends_text = " and ".join(depends_on) if depends_on else "carry only"
            decision_trace.append({
                "column": col + 1,
                "role": "result",
                "char": char,
                "chosen": target_digit,
                "reason": "forced",
                "depends_on": depends_on,
                "note": f"{depends_text} -> column sum {col_sum}, {char} = {col_sum} % 10 = {target_digit} (carry_in={carry})",
            })

            if solve(col + 1, 0, next_carry):
                return True

            del assigned[char]
            used_digits.remove(target_digit)
            backtracks += 1
            decision_trace.pop()
            return False

        # Addend rows (0 or 1)
        else:
            if col >= len(words[row]):
                return solve(col, row + 1, carry)

            char = words[row][col]
            if char in assigned:
                return solve(col, row + 1, carry)

            # Try digits with a simple heuristic: prefer digits that are not used and
            # try non-zero first when char is leading.
            digits = list(range(10))
            # heuristic: try smaller set first (non-used)
            eliminated: List[Dict[str, Union[int, str]]] = []
            for digit in digits:
                if digit in used_digits:
                    owner = next((k for k, v in assigned.items() if v == digit), None)
                    reason = f"already taken by {owner}" if owner is not None else "already assigned to another letter"
                    eliminated.append({"digit": digit, "reason": reason})
                    continue
                if digit == 0 and char in leading_chars:
                    eliminated.append({"digit": digit, "reason": "leading digit cannot be 0"})
                    continue
                assigned[char] = digit
                used_digits.add(digit)
                assignments += 1
                decision_trace.append({
                    "column": col + 1,
                    "role": "addend" if row == 0 else "addend2",
                    "char": char,
                    "chosen": digit,
                    "reason": "chosen",
                    "eliminated": list(eliminated),
                })

                if solve(col, row + 1, carry):
                    return True

                del assigned[char]
                used_digits.remove(digit)
                backtracks += 1
                decision_trace.pop()
                eliminated.append({"digit": digit, "reason": "led to a dead end further down the search"})

            return False

    # start search
    solve(0, 0, 0)

    elapsed = time.monotonic() - start_time
    metrics: Dict[
        str,
        Union[int, float, List[Dict[str, Union[int, str]]], Dict[str, Union[int, str]]],
    ] = {
        "elapsed_seconds": elapsed,
        "recursive_calls": calls,
        "assignments": assignments,
        "backtracks": backtracks,
        "solutions_found": len(solutions),
    }

    if collect_metrics:
        leading_bound = _derive_leading_bound(word1, word2, result)
        if leading_bound is not None:
            metrics["leading_bound"] = leading_bound

    if collect_metrics and solutions:
        # Pick the fastest-reached solution (lowest recursive-call count at time of discovery).
        # All recorded solutions are already 100% valid by construction (only appended when
        # carry == 0 on the final column), so "fastest" is the only real selection criterion.
        fastest = min(trace_snapshots, key=lambda s: s["calls_to_reach"])
        fastest_idx = fastest["solution_index"]
        fastest_sol = solutions[fastest_idx]

        metrics["fastest_solution_index"] = fastest_idx
        metrics["solution_steps"] = _derive_solution_steps(word1, word2, result, fastest_sol)
        metrics["reasoning_steps"] = fastest["trace"]

    if collect_metrics:
        if return_all:
            return solutions, metrics
        return (solutions[0] if solutions else None), metrics

    if return_all:
        return solutions
    return solutions[0] if solutions else None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crypto-arithmetic solver")
    parser.add_argument("word1")
    parser.add_argument("word2")
    parser.add_argument("result")
    parser.add_argument("--all", action="store_true", help="Return all solutions")
    parser.add_argument("--timeout", type=float, default=None, help="Timeout in seconds")
    parser.add_argument("--max-solutions", type=int, default=None)
    parser.add_argument("--metrics-json", type=str, default=None, help="Write solutions+metrics to JSON file")
    args = parser.parse_args()

    if args.metrics_json:
        sols, metrics = solve_cryptarithmetic_optimized(  # type: ignore[misc]
            args.word1,
            args.word2,
            args.result,
            return_all=args.all,
            max_solutions=args.max_solutions,
            timeout=args.timeout,
            collect_metrics=True,
        )
        import json

        out = {"solutions": sols, "metrics": metrics}
        with open(args.metrics_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(args.metrics_json)
    else:
        sol = solve_cryptarithmetic_optimized(
            args.word1, args.word2, args.result, return_all=args.all, max_solutions=args.max_solutions, timeout=args.timeout
        )
        print(sol)