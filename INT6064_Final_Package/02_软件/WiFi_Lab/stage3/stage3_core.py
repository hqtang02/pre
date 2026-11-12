"""Shared scoring rules. Costs and coordinates have one source: data.py."""
import math
from itertools import combinations
from data import (CLASSROOMS, ROUTERS, COVERAGE_RADIUS, ROUTER_LIMIT,
                  INSTALLATION_COSTS, ROUTER_COVERAGE)

COVERAGE_WEIGHT = 0.70
COST_WEIGHT = 0.30
WEIGHT_PRESETS = {"Coverage priority 100/0": 1.0,
                  "Balanced 70/30": 0.7,
                  "Cost priority 30/70": 0.3}


def validate_weight(weight):
    if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 <= weight <= 1:
        raise ValueError("Coverage weight must be a finite number between 0 and 1.")


def valid_plan(selected):
    return (isinstance(selected, (list, tuple)) and len(selected) == ROUTER_LIMIT
            and all(type(r) is str and r in ROUTERS for r in selected)
            and len(set(selected)) == ROUTER_LIMIT)


def calculate_coverage(selected):
    covered = set()
    for router in selected:
        covered.update(ROUTER_COVERAGE[router])
    return [c for c in CLASSROOMS if c in covered]


def calculate_cost(selected):
    return sum(INSTALLATION_COSTS[r] for r in selected)


def get_max_cost():
    """Normalization reference, not a budget constraint."""
    return sum(sorted(INSTALLATION_COSTS.values())[-ROUTER_LIMIT:])


def evaluate_plan(selected, coverage_weight=0.70):
    if not valid_plan(selected):
        raise ValueError("Return exactly 3 different valid router IDs.")
    validate_weight(coverage_weight)
    covered = calculate_coverage(selected)
    cost = calculate_cost(selected)
    rate = len(covered) / len(CLASSROOMS)
    cost_score = 1 - cost / get_max_cost()
    return dict(routers=tuple(sorted(selected)), covered=covered,
                uncovered=[c for c in CLASSROOMS if c not in covered],
                covered_count=len(covered), coverage_rate=rate, cost=cost,
                cost_score=cost_score, coverage_weight=coverage_weight,
                score=coverage_weight * rate + (1-coverage_weight)*cost_score)


def find_best_plan(coverage_weight=0.70):
    validate_weight(coverage_weight)
    plans = [evaluate_plan(p, coverage_weight)
             for p in combinations(sorted(ROUTERS), ROUTER_LIMIT)]
    plans.sort(key=lambda p: (-p['score'], p['cost'], p['routers']))
    return plans[0], plans


def verify_optimal(selected, coverage_weight=0.70):
    """Accept every plan tied for top score, regardless of cost or ID order."""
    if not valid_plan(selected):
        return False
    best, _ = find_best_plan(coverage_weight)
    return math.isclose(evaluate_plan(selected, coverage_weight)['score'],
                        best['score'], rel_tol=1e-9, abs_tol=1e-9)
