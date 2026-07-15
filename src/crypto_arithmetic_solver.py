from typing import Dict, Optional, List, Union, Tuple, overload
try:
    from typing import Literal
except Exception:
    from typing_extensions import Literal
import time


def derive_solution_steps(word1: str, word2: str, result: str, mapping: Dict[str, int]) -> List[Dict[str, Union[int, str]]]:
    """Reconstruct a human-readable, column-by-column derivation for an already-found solution.

    Replays the accepted mapping right-to-left (units column first, matching how the
    solver actually works) and explains each column's arithmetic. Contains no
    backtracked/rejected attempts -- only the final, accepted values.

    Returns a list of step dicts, one per column, e.g.:
        {
            "column": 0,
            "description": "column 0 (units): D + E = 7 + 5 = 12 -> digit 2, carry 1",
            "carry_in": 0,
            "carry_out": 1,
            "digit": 2,
        }
    """
    w1, w2, w3 = word1.upper()[::-1], word2.upper()[::-1], result.upper()[::-1]
    steps: List[Dict[str, Union[int, str]]] = []
    carry = 0
    col_names = ["units", "tens", "hundreds", "thousands", "ten-thousands"]

    for col in range(len(w3)):
        ch0 = w1[col] if col < len(w1) else None
        ch1 = w2[col] if col < len(w2) else None
        ch_res = w3[col]

        d0 = mapping[ch0] if ch0 is not None else None
        d1 = mapping[ch1] if ch1 is not None else None
        d_res = mapping[ch_res]

        col_sum = carry + (d0 or 0) + (d1 or 0)
        next_carry = col_sum // 10

        place = col_names[col] if col < len(col_names) else f"10^{col}"

        terms = []
        if d0 is not None:
            terms.append(f"{ch0}({d0})")
        if d1 is not None:
            terms.append(f"{ch1}({d1})")
        addends_str = " + ".join(terms)

        if terms:
            carry_str = f" + carry {carry}" if carry else ""
            lhs = f"{addends_str}{carry_str}"
        else:
            lhs = f"carry {carry}"

        description = (
            f"column {col} ({place}): {lhs} = {col_sum} "
            f"-> {ch_res} = {d_res}, carry {next_carry}"
        )

        steps.append({
            "column": col,
            "description": description,
            "carry_in": carry,
            "carry_out": next_carry,
            "digit": d_res,
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
) -> Tuple[Optional[Dict[str, int]], Dict[str, Union[int, float, List[Dict[str, Union[int, str]]]]]]:
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
) -> Tuple[List[Dict[str, int]], Dict[str, Union[int, float, List[Dict[str, Union[int, str]]]]]]:
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
    Tuple[Optional[Dict[str, int]], Dict[str, Union[int, float, List[Dict[str, Union[int, str]]]]]],
    Tuple[List[Dict[str, int]], Dict[str, Union[int, float, List[Dict[str, Union[int, str]]]]]],
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
                if not return_all:
                    return True
                if max_solutions is not None and len(solutions) >= max_solutions:
                    return True
            return False

        # Result row (row == 2)
        if row == 2:
            col_sum = carry
            if col < len(words[0]):
                ch0 = words[0][col]
                if ch0 not in assigned:
                    return False
                col_sum += assigned[ch0]
            if col < len(words[1]):
                ch1 = words[1][col]
                if ch1 not in assigned:
                    return False
                col_sum += assigned[ch1]

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

            if solve(col + 1, 0, next_carry):
                return True

            del assigned[char]
            used_digits.remove(target_digit)
            backtracks += 1
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
            for digit in digits:
                if digit in used_digits:
                    continue
                if digit == 0 and char in leading_chars:
                    continue
                assigned[char] = digit
                used_digits.add(digit)
                assignments += 1

                if solve(col, row + 1, carry):
                    return True

                del assigned[char]
                used_digits.remove(digit)
                backtracks += 1

            return False

    # start search
    solve(0, 0, 0)

    elapsed = time.monotonic() - start_time
    best_solution = solutions[0] if solutions else None
    metrics = {
        "elapsed_seconds": elapsed,
        "recursive_calls": calls,
        "assignments": assignments,
        "backtracks": backtracks,
        "solutions_found": len(solutions),
        "solution_steps": derive_solution_steps(word1, word2, result, best_solution) if best_solution else [],
    }

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