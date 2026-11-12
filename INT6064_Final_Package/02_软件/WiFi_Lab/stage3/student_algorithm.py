"""Optional file-based TODO 6 exercise; the GUI keeps its own editor drafts.
Copy only the function body into the GUI free-coding box, not imports or def.
This template intentionally contains unfinished tasks.
"""
from itertools import combinations
from data import (CLASSROOMS, ROUTERS, ROUTER_LIMIT, ROUTER_COVERAGE, INSTALLATION_COSTS)
from stage3_core import get_max_cost, validate_weight


def find_optimal_plan(coverage_weight=0.70):
    validate_weight(coverage_weight)
    cost_weight = 1 - coverage_weight
    MAX_COST = get_max_cost()
    best_plan = None
    best_score = -1
    for selected in combinations(sorted(ROUTERS), ROUTER_LIMIT):
        # A: build a set named covered, merging the coverage of selected routers.
        # B: calculate coverage_rate, total_cost, cost_score and score.
        # C: update best_score AND best_plan when the current score is better.
        pass
    return best_plan
