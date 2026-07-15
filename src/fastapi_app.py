from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.crypto_arithmetic_solver import solve_cryptarithmetic_optimized

app = FastAPI()


class Puzzle(BaseModel):
    word1: str
    word2: str
    result: str
    all: Optional[bool] = False
    timeout: Optional[float] = None


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
