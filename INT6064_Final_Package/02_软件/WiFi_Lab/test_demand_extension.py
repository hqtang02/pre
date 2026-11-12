import unittest
from demand_extension import evaluate,all_plans,budget_best,pareto,DEMAND

class DemandTests(unittest.TestCase):
    def test_total_and_full_coverage(self):
        self.assertEqual(sum(DEMAND.values()),410)
        self.assertEqual(evaluate('BDE')['people'],410)
    def test_dedup_and_metrics(self):
        r=evaluate('BDG');self.assertEqual(r['people'],385)
        self.assertEqual(r['points'],11);self.assertEqual(r['cost'],750)
        self.assertAlmostEqual(r['population_rate'],385/410)
    def test_all_combinations(self):
        rows=all_plans();self.assertEqual(len(rows),35)
        self.assertEqual(len({r['plan'] for r in rows}),35)
    def test_budget_boundary_and_infeasible(self):
        self.assertEqual(budget_best(all_plans(),529),[])
        self.assertEqual([r['plan'] for r in budget_best(all_plans(),530)],['ACG'])
        self.assertEqual([r['plan'] for r in budget_best(all_plans(),750)],['BDG'])
    def test_invalid_selection(self):
        for p in ['', 'BD', 'BBG', 'BDH', 'ABDG']:
            with self.assertRaises(ValueError):evaluate(p)
    def test_pareto_and_ties(self):
        rows=[dict(cost=1,people=5),dict(cost=1,people=5),dict(cost=2,people=5),dict(cost=2,people=6)]
        self.assertEqual(pareto(rows),[rows[0],rows[1],rows[3]])
        self.assertEqual(len(budget_best(rows,1)),2)
    def test_full_budget(self):
        self.assertEqual([r['plan'] for r in budget_best(all_plans(),1100)],['BDE'])
if __name__=='__main__':unittest.main()
