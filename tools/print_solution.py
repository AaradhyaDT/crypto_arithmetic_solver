#!/usr/bin/env python3
"""Print a human-friendly summary for a solver metrics JSON file.

Usage: python tools/print_solution.py reports/solution_xxx.json --words WORD1 WORD2 RESULT
"""
import argparse
import json
from pathlib import Path
from typing import Dict, Any


def numeric_value(word: str, mapping: Dict[str, int]) -> str:
    try:
        return ''.join(str(mapping[c]) for c in word)
    except KeyError:
        return '<missing mapping>'


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('json_path', type=Path)
    p.add_argument('--words', nargs=3, help='Three words: addend1 addend2 result', metavar='WORD')
    args = p.parse_args()

    data: Dict[str, Any] = json.loads(args.json_path.read_text(encoding='utf-8'))
    sols = data.get('solutions')
    metrics = data.get('metrics', {})

    # solutions may be a dict (single mapping) or a list
    fastest_idx = metrics.get('fastest_solution_index', 0)
    if isinstance(sols, dict):
        mapping = sols
    elif isinstance(sols, list) and sols:
        mapping = sols[fastest_idx] if fastest_idx < len(sols) else sols[0]
    else:
        mapping = None

    print('\n=== Solution Summary ===')
    if mapping is None:
        print('No solution found in file:', args.json_path)
    else:
        print('Mapping:')
        for k in sorted(mapping.keys()):
            print(f'  {k} -> {mapping[k]}')

        if args.words:
            w1, w2, res = args.words
            n1 = numeric_value(w1.upper(), mapping)
            n2 = numeric_value(w2.upper(), mapping)
            nr = numeric_value(res.upper(), mapping)
            print('\nNumeric:')
            print(f'  {w1} -> {n1}')
            print(f'  {w2} -> {n2}')
            print(f'  {res} -> {nr}')
            if n1.isdigit() and n2.isdigit() and nr.isdigit():
                print(f'\nCheck: {n1} + {n2} = {nr} -> {int(n1) + int(n2) == int(nr)}')

    leading_bound = metrics.get('leading_bound')
    if leading_bound:
        print('\n=== Deduced Bound (before search) ===')
        print(f"  Column {leading_bound['column']}: {leading_bound['note']}")

    reasoning_steps = metrics.get('reasoning_steps')
    if reasoning_steps:
        print('\n=== Reasoning (why each digit) ===')
        for step in reasoning_steps:
            if step['reason'] == 'forced':
                print(f"  Column {step['column']} [{step['role']}]: {step['char']} = {step['chosen']} -- {step['note']}")
            else:
                print(f"  Column {step['column']} [{step['role']}]: {step['char']} = {step['chosen']}")
                for e in step.get('eliminated', []):
                    print(f"      ruled out {e['digit']}: {e['reason']}")

    solution_steps = metrics.get('solution_steps')
    if solution_steps:
        print('\n=== Solving Steps ===')
        for step in solution_steps:
            print(f"  Column {step['column']}: {step['equation']}")

    print('\n=== Metrics ===')
    skip_keys = {'solution_steps', 'reasoning_steps', 'leading_bound', 'fastest_solution_index'}
    for k in sorted(metrics.keys()):
        if k in skip_keys:
            continue
        print(f'  {k}: {metrics[k]}')


if __name__ == '__main__':
    main()