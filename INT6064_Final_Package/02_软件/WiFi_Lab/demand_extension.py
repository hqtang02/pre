"""Optional teacher CLI: population coverage, budget constraint, Pareto comparison.
Uses the SAME fixed-three-router data and costs as the main lab. No GUI changes.
"""
from itertools import combinations
from pathlib import Path
import argparse
import csv
from stage3.data import CLASSROOMS, ROUTERS, ROUTER_COVERAGE, INSTALLATION_COSTS

DEMAND = dict(zip(CLASSROOMS, [40,30,25,35,45,30,30,50,35,20,40,30]))

def evaluate(plan):
    plan = tuple(plan)
    if len(plan) != 3 or len(set(plan)) != 3 or any(r not in ROUTERS for r in plan):
        raise ValueError('Choose exactly three distinct valid positions.')
    covered = set().union(*(set(ROUTER_COVERAGE[r]) for r in plan))
    people = sum(DEMAND[c] for c in covered)
    return dict(plan=''.join(sorted(plan)), points=len(covered), people=people,
                population_rate=people/sum(DEMAND.values()), point_rate=len(covered)/len(CLASSROOMS),
                cost=sum(INSTALLATION_COSTS[r] for r in plan),
                missing=','.join(c for c in CLASSROOMS if c not in covered))

def all_plans():
    return [evaluate(p) for p in combinations(sorted(ROUTERS),3)]

def budget_best(rows, budget):
    feasible = [r for r in rows if r['cost'] <= budget]
    if not feasible: return []
    best = max(r['people'] for r in feasible)
    return [r for r in feasible if r['people'] == best]

def pareto(rows):
    return [r for r in rows if not any(
        t['cost'] <= r['cost'] and t['people'] >= r['people'] and
        (t['cost'] < r['cost'] or t['people'] > r['people']) for t in rows)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget',type=float,default=750)
    parser.add_argument('--csv',type=Path)
    args=parser.parse_args()
    if not 0 <= args.budget < float('inf'):parser.error('budget must be finite and non-negative')
    rows=all_plans()
    print('OPTIONAL MODEL | exactly 3 routers | current installation costs | total people',sum(DEMAND.values()))
    for r in rows:print(r)
    print('Budget:',args.budget,'Best population coverage:',budget_best(rows,args.budget) or 'No feasible plan')
    print('Pareto front:',pareto(rows))
    if args.csv:
        with args.csv.open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        print('CSV saved:',args.csv)

if __name__ == '__main__':main()
