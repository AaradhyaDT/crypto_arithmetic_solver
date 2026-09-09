"""Crypto-arithmetic solver and checker package."""
from src.crypto_arithmetic_solver import (
    solve_cryptarithmetic_optimized,
    check_solution,
    check_solutions,
    parse_mapping,
    parse_mappings,
    parse_answer,
    load_mapping_from_json,
    load_mappings_from_json,
)

__all__ = [
    "solve_cryptarithmetic_optimized",
    "check_solution",
    "check_solutions",
    "parse_mapping",
    "parse_mappings",
    "parse_answer",
    "load_mapping_from_json",
    "load_mappings_from_json",
]
