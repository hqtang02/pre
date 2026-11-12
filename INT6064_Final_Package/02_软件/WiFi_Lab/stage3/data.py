GRID_SIZE = 10
COVERAGE_RADIUS = 3
ROUTER_LIMIT = 3

CLASSROOMS = {
    "C1": (2, 4),
    "C2": (6, 9),
    "C3": (1, 3),
    "C4": (6, 1),
    "C5": (4, 9),
    "C6": (3, 8),
    "C7": (5, 2),
    "C8": (4, 6),
    "C9": (8, 3),
    "C10": (1, 4),
    "C11": (6, 3),
    "C12": (4, 1),
}

ROUTERS = {
    "A": (3, 4),
    "B": (8, 1),
    "C": (1, 7),
    "D": (6, 8),
    "E": (2, 2),
    "F": (6, 5),
    "G": (4, 4),
}

INSTALLATION_COSTS = {
    "A": 250,
    "B": 300,
    "C": 180,
    "D": 350,
    "E": 450,
    "F": 260,
    "G": 100,
}

# Automatically calculate which classrooms
# each router can cover.
ROUTER_COVERAGE = {}

for rid, (rx, ry) in ROUTERS.items():
    covered = []

    for cid, (cx, cy) in CLASSROOMS.items():
        distance_squared = (
            (cx - rx) ** 2 + (cy - ry) ** 2
        )

        if distance_squared <= COVERAGE_RADIUS ** 2:
            covered.append(cid)

    ROUTER_COVERAGE[rid] = covered