
import unittest

from data import CLASSROOMS, ROUTERS
from coverage import is_covered, calculate_coverage


class TestWiFiCoverage(unittest.TestCase):

    def test_T1_optimal_solution(self):
        """BDE must cover all 12 classrooms."""
        result = calculate_coverage(["B", "D", "E"])
        self.assertEqual(result["count"], 12)
        self.assertEqual(result["rate"], 100.0)
        self.assertEqual(result["uncovered"], [])

    def test_T2_greedy_solution(self):
        """GDB must cover 11 classrooms."""
        result = calculate_coverage(["G", "D", "B"])
        self.assertEqual(result["count"], 11)
        self.assertEqual(result["uncovered"], ["C3"])

    def test_T3_boundary_covered(self):
        """Distance squared = 9 must be covered."""
        self.assertTrue(
            is_covered(CLASSROOMS["C6"], ROUTERS["D"])
        )

    def test_T4_outside_radius(self):
        """Distance squared = 10 must not be covered."""
        self.assertFalse(
            is_covered(CLASSROOMS["C3"], ROUTERS["G"])
        )

    def test_T5_duplicate_router(self):
        """Duplicate router selections must be rejected."""
        with self.assertRaises(ValueError):
            calculate_coverage(["B", "B", "D"])

    def test_T6_too_few_routers(self):
        """Fewer than 3 routers must be rejected."""
        with self.assertRaises(ValueError):
            calculate_coverage(["B", "D"])

    def test_T7_too_many_routers(self):
        """More than 3 routers must be rejected."""
        with self.assertRaises(ValueError):
            calculate_coverage(["A", "B", "D", "E"])

    def test_T8_invalid_router(self):
        """Unknown router IDs must be rejected."""
        with self.assertRaises(ValueError):
            calculate_coverage(["B", "D", "H"])

    def test_T9_no_duplicate_classroom_count(self):
        """Each classroom must be counted only once."""
        result = calculate_coverage(["B", "D", "E"])
        self.assertEqual(
            len(result["covered"]),
            len(set(result["covered"]))
        )

    def test_T10_all_classrooms_accounted_for(self):
        """Covered and uncovered counts must total 12."""
        result = calculate_coverage(["A", "C", "F"])
        self.assertEqual(
            len(result["covered"]) + len(result["uncovered"]),
            12
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
