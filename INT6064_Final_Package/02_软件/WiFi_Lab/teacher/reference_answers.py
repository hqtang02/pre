"""Teacher-only reference. Not imported by the student GUI."""
EXPRESSIONS = {
    3: 'costs[selected[0]] + costs[selected[1]] + costs[selected[2]]',
    4: 'coverage_weight * coverage_rate + cost_weight * cost_score',
    5: 'score > best_score',
}
BLOCKS = {
    'A': 'covered = set()\nfor router in selected:\n    covered.update(ROUTER_COVERAGE[router])',
    'B': 'coverage_rate = len(covered) / len(CLASSROOMS)\ntotal_cost = student_cost(selected)\ncost_score = 1 - total_cost / MAX_COST\nscore = student_score(coverage_rate, cost_score)',
    'C': 'if student_better(score, best_score):\n    best_score = score\n    best_plan = selected',
}
DEBUG_REPAIRS = {
    'Overlap': BLOCKS['A'] + '\ncovered_count = len(covered)',
    'Comparison': 'if score > best_score:\n    best_score = score\n    best_plan = selected',
}
# Standalone function body matching the student's submitted answer.
FREE_ALGORITHM = '''best_plan = None
best_score = -1
router_ids = sorted(ROUTERS)
for selected in combinations(router_ids, ROUTER_LIMIT):
    covered = set()
    for router in selected:
        covered.update(ROUTER_COVERAGE[router])
    coverage_rate = len(covered) / len(CLASSROOMS)
    total_cost = 0
    for router in selected:
        total_cost += INSTALLATION_COSTS[router]
    cost_score = 1 - total_cost / MAX_COST
    score = coverage_weight * coverage_rate + cost_weight * cost_score
    if score > best_score:
        best_score = score
        best_plan = selected
return best_plan'''
BASIC_EXPRESSIONS = ('(cx-rx)**2 + (cy-ry)**2', 'distance_squared <= COVERAGE_RADIUS**2')
