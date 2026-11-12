
# coverage.py

from data import CLASSROOMS, ROUTERS, COVERAGE_RADIUS, ROUTER_LIMIT


def is_covered(classroom_pos, router_pos):
    """Check whether a router covers a classroom point."""
    cx, cy = classroom_pos
    rx, ry = router_pos

    distance_squared = (cx - rx) ** 2 + (cy - ry) ** 2
    return distance_squared <= COVERAGE_RADIUS ** 2


def calculate_coverage(selected_routers):
    """Calculate coverage for a set of router positions."""
    selected = list(selected_routers)

    # Check valid input
    if len(selected) != ROUTER_LIMIT:
        raise ValueError("Exactly 3 routers must be selected.")

    if len(set(selected)) != ROUTER_LIMIT:
        raise ValueError("Router positions must be different.")

    for router in selected:
        if router not in ROUTERS:
            raise ValueError(f"Invalid router position: {router}")

    covered = []
    uncovered = []

    for classroom_id, classroom_pos in CLASSROOMS.items():
        covered_by_any = False

        for router_id in selected:
            router_pos = ROUTERS[router_id]

            if is_covered(classroom_pos, router_pos):
                covered_by_any = True
                break

        if covered_by_any:
            covered.append(classroom_id)
        else:
            uncovered.append(classroom_id)

    coverage_count = len(covered)
    coverage_rate = coverage_count / len(CLASSROOMS) * 100

    return {
        "selected": selected,
        "covered": covered,
        "uncovered": uncovered,
        "count": coverage_count,
        "rate": coverage_rate
    }


if __name__ == "__main__":
    for selected in [
        ["B", "D", "E"],
        ["G", "D", "B"]
    ]:
        result = calculate_coverage(selected)

        print("=" * 45)
        print("Selected routers:", result["selected"])
        print("Covered classrooms:", result["covered"])
        print("Uncovered classrooms:", result["uncovered"])
        print("Coverage count:", result["count"])
        print(f"Coverage rate: {result['rate']:.2f}%")
