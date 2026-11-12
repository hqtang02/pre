
# coverage.py
# INT6064 - Student Coding Exercise

from data import (
    CLASSROOMS,
    ROUTERS,
    COVERAGE_RADIUS,
    ROUTER_LIMIT
)


def is_covered(classroom_pos, router_pos):
    """
    STUDENT EXERCISE

    Learning objectives:
    1. Calculate squared distance.
    2. Use a conditional expression.
    3. Determine Wi-Fi coverage.

    Coverage rule:
    d² = (cx-rx)² + (cy-ry)²

    A classroom is covered when:
    d² <= R²
    """

    cx, cy = classroom_pos
    rx, ry = router_pos

    # Optional file exercise. The GUI has separate expression editors.
    # TODO 1: calculate distance_squared using cx, cy, rx and ry.
    # TODO 2: return whether distance_squared <= COVERAGE_RADIUS ** 2.
    raise NotImplementedError("Complete TODO 1 and TODO 2, or use gui.py.")


def calculate_coverage(selected_routers):
    """
    Calculate classroom coverage for
    exactly three different routers.
    """

    selected = list(selected_routers)

    # Check router quantity
    if len(selected) != ROUTER_LIMIT:
        raise ValueError(
            "Exactly 3 routers must be selected."
        )

    # Reject duplicate positions
    if len(set(selected)) != ROUTER_LIMIT:
        raise ValueError(
            "Router positions must be different."
        )

    # Validate router IDs
    for router in selected:
        if router not in ROUTERS:
            raise ValueError(
                f"Invalid router position: {router}"
            )

    covered = []
    uncovered = []

    # Check each classroom
    for classroom_id, classroom_pos in CLASSROOMS.items():

        covered_by_any = False

        # Check selected routers
        for router_id in selected:

            router_pos = ROUTERS[router_id]

            if is_covered(classroom_pos, router_pos):
                covered_by_any = True
                break

        # Count each classroom only once
        if covered_by_any:
            covered.append(classroom_id)
        else:
            uncovered.append(classroom_id)

    coverage_count = len(covered)

    coverage_rate = (
        coverage_count / len(CLASSROOMS) * 100
    )

    return {
        "selected": selected,
        "covered": covered,
        "uncovered": uncovered,
        "count": coverage_count,
        "rate": coverage_rate
    }


if __name__ == "__main__":

    print("INT6064 - Student Coverage Test")
    print("=" * 45)

    test_cases = [
        ["B", "D", "E"],
        ["G", "D", "B"]
    ]

    for selected in test_cases:

        result = calculate_coverage(selected)

        print("-" * 45)
        print("Selected routers:", result["selected"])
        print("Covered classrooms:", result["covered"])
        print("Uncovered classrooms:", result["uncovered"])
        print("Coverage count:", result["count"])
        print(
            f"Coverage rate: {result['rate']:.2f}%"
        )
