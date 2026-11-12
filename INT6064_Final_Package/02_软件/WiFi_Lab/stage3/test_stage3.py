
import unittest

from stage3_core import (
    calculate_cost,
    calculate_coverage,
    evaluate_plan,
    find_best_plan,
    get_max_cost,
)


class TestStage3(unittest.TestCase):

    def test_cost_bdg(self):
        self.assertEqual(
            calculate_cost(("B", "D", "G")), 750
        )

    def test_cost_bde(self):
        self.assertEqual(
            calculate_cost(("B", "D", "E")), 1100
        )

    def test_coverage_bdg(self):
        self.assertEqual(
            len(calculate_coverage(("B", "D", "G"))), 11
        )

    def test_coverage_bde(self):
        self.assertEqual(
            len(calculate_coverage(("B", "D", "E"))), 12
        )

    def test_max_cost(self):
        self.assertEqual(get_max_cost(), 1100)

    def test_bdg_score(self):
        plan = evaluate_plan(("B", "D", "G"))
        self.assertAlmostEqual(
            plan["score"] * 100, 73.7121212121, places=5
        )

    def test_bde_score(self):
        plan = evaluate_plan(("B", "D", "E"))
        self.assertAlmostEqual(
            plan["score"] * 100, 70.0
        )

    def test_invalid_router_count(self):
        with self.assertRaises(ValueError):
            evaluate_plan(("B", "D"))

    def test_duplicate_router(self):
        with self.assertRaises(ValueError):
            evaluate_plan(("B", "B", "D"))

    def test_unknown_router(self):
        with self.assertRaises(ValueError):
            evaluate_plan(("B", "D", "Z"))

    def test_all_combinations(self):
        best, plans = find_best_plan()
        self.assertEqual(len(plans), 35)

    def test_optimal_plan(self):
        best, plans = find_best_plan()
        self.assertEqual(
            best["routers"], ("B", "D", "G")
        )

    def test_unique_top_score(self):
        best, plans = find_best_plan()
        self.assertGreater(
            best["score"], plans[1]["score"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
