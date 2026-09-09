from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, List, Union
from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized, check_solution, check_solutions

app = FastAPI()


class Puzzle(BaseModel):
    word1: str
    word2: str
    result: str
    all: Optional[bool] = False
    timeout: Optional[float] = None


class CheckPuzzle(BaseModel):
    word1: str
    word2: str
    result: str
    mapping: Optional[Dict[str, Union[int, str]]] = None
    mappings: Optional[List[Dict[str, Union[int, str]]]] = None


@app.post("/solve")
def solve(p: Puzzle, metrics: Optional[bool] = False):
    """Solve puzzle. If `metrics=true` is provided as a query parameter, return metrics too.

    Examples:
    - POST /solve with JSON body -> returns {"solutions": ...}
    - POST /solve?metrics=1 -> returns {"solutions": ..., "metrics": {...}}
    """
    if metrics:
        sols, m = solve_cryptarithmetic_optimized(p.word1, p.word2, p.result, return_all=p.all, timeout=p.timeout, collect_metrics=True)
        return {"solutions": sols, "metrics": m}
    sol = solve_cryptarithmetic_optimized(p.word1, p.word2, p.result, return_all=p.all, timeout=p.timeout)
    return {"solutions": sol}


@app.post("/check")
def check(p: CheckPuzzle):
    """Check if one or multiple candidate mappings solve the cryptarithmetic puzzle.

    Examples:
    - Single solution:
      POST /check with body {"word1": "SEND", "word2": "MORE", "result": "MONEY", "mapping": {...}}
      -> returns {"valid": true, "message": "OK: 9567 + 1085 = 10652"}
    - Multiple solutions:
      POST /check with body {"word1": "TWO", "word2": "TWO", "result": "FOUR", "mappings": [{...}, {...}]}
      -> returns {"valid": true, "total": 2, "valid_count": 2, "results": [...]}
    """
    if p.mappings is not None and len(p.mappings) > 1:
        results = []
        valid_count = 0
        for m in p.mappings:
            v, msg = check_solution(p.word1, p.word2, p.result, m)
            if v:
                valid_count += 1
            results.append({"valid": v, "message": msg})
        return {
            "valid": valid_count == len(p.mappings),
            "total": len(p.mappings),
            "valid_count": valid_count,
            "results": results,
        }

    target_mapping = p.mapping if p.mapping is not None else (p.mappings[0] if p.mappings else None)
    valid, msg = check_solution(p.word1, p.word2, p.result, target_mapping)
    return {"valid": valid, "message": msg}

