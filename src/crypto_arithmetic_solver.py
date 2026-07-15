from typing import Dict, Optional, List, Union, Tuple
import time


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
    metrics = {
        "elapsed_seconds": elapsed,
        "recursive_calls": calls,
        "assignments": assignments,
        "backtracks": backtracks,
        "solutions_found": len(solutions),
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