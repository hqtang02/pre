
import ast
import math
import operator
import tkinter as tk
from tkinter import ttk, messagebox

from data import CLASSROOMS, ROUTERS, COVERAGE_RADIUS

# =====================================================
# 1. Safe Python expression evaluator
# =====================================================

BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Pow: operator.pow,
}

COMPARE_OPS = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
}

ALLOWED_NAMES = {
    "cx", "cy", "rx", "ry",
    "distance_squared", "COVERAGE_RADIUS"
}


def safe_evaluate(expression, variables):
    if not expression.strip():
        raise ValueError("Please complete the TODO.")

    if len(expression) > 150:
        raise ValueError("Expression is too long.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node, depth=0):
        if depth > 20:
            raise ValueError("Expression is too complex.")

        if isinstance(node, ast.Expression):
            return evaluate(node.body, depth + 1)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float, bool):
                if type(node.value) in (int, float):
                    if not math.isfinite(node.value):
                        raise ValueError("Invalid number.")
                    if abs(node.value) > 10000:
                        raise ValueError("Number is too large.")
                return node.value

        if isinstance(node, ast.Name):
            if node.id in ALLOWED_NAMES:
                if node.id in variables:
                    return variables[node.id]
            raise ValueError(
                f"Variable '{node.id}' is not allowed."
            )

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in BINARY_OPS:
                raise ValueError("Operator not allowed.")

            left = evaluate(node.left, depth + 1)
            right = evaluate(node.right, depth + 1)

            if type(left) not in (int, float):
                raise ValueError("Expected a number.")
            if type(right) not in (int, float):
                raise ValueError("Expected a number.")

            if op_type is ast.Pow:
                if abs(right) > 4 or abs(left) > 10000:
                    raise ValueError("Power is too large.")

            value = BINARY_OPS[op_type](left, right)

            if not math.isfinite(value) or abs(value) > 1e12:
                raise ValueError("Result is too large.")

            return value

        if isinstance(node, ast.Compare):
            if len(node.ops) != 1:
                raise ValueError("Use one comparison.")

            left = evaluate(node.left, depth + 1)
            right = evaluate(node.comparators[0], depth + 1)

            op_type = type(node.ops[0])

            if op_type not in COMPARE_OPS:
                raise ValueError("Comparison not allowed.")

            return COMPARE_OPS[op_type](left, right)

        raise ValueError("Unsupported Python expression.")

    return evaluate(tree)


# =====================================================
# 2. Student expressions
# =====================================================

def get_expressions():
    distance_expr = distance_editor.get(
        "1.0", "end"
    ).strip()

    condition_expr = condition_editor.get(
        "1.0", "end"
    ).strip()

    return distance_expr, condition_expr


def calculate_student_distance(classroom, router):
    cx, cy = classroom
    rx, ry = router

    distance_expr, _ = get_expressions()

    variables = {
        "cx": cx,
        "cy": cy,
        "rx": rx,
        "ry": ry,
        "COVERAGE_RADIUS": COVERAGE_RADIUS
    }

    value = safe_evaluate(distance_expr, variables)

    if type(value) not in (int, float):
        raise ValueError(
            "TODO 1 must produce a number."
        )

    return value


def calculate_student_condition(distance_squared):
    _, condition_expr = get_expressions()

    # Only these variables are available in TODO 2.
    variables = {
        "distance_squared": distance_squared,
        "COVERAGE_RADIUS": COVERAGE_RADIUS
    }

    value = safe_evaluate(condition_expr, variables)

    if type(value) is not bool:
        raise ValueError(
            "TODO 2 must produce True or False."
        )

    return value


def student_is_covered(classroom, router):
    distance_squared = calculate_student_distance(
        classroom, router
    )

    return calculate_student_condition(distance_squared)


# =====================================================
# 3. Independent verification
# =====================================================

def expected_distance(classroom, router):
    cx, cy = classroom
    rx, ry = router

    return (cx-rx)**2 + (cy-ry)**2


def verify_student_pair(classroom, router):
    expected_d = expected_distance(classroom, router)

    actual_d = calculate_student_distance(
        classroom, router
    )

    if not math.isclose(
        actual_d, expected_d,
        rel_tol=0,
        abs_tol=1e-9
    ):
        raise ValueError(
            "TODO 1 incorrect: expected squared "
            f"distance {expected_d}, got {actual_d}."
        )

    actual_covered = calculate_student_condition(
        actual_d
    )

    expected_covered = (
        expected_d <= COVERAGE_RADIUS**2
    )

    if actual_covered != expected_covered:
        raise ValueError(
            "TODO 2 incorrect: expected "
            f"{expected_covered}, got {actual_covered}."
        )

    return actual_covered


def student_calculate(selected_routers):
    if len(selected_routers) != 3:
        raise ValueError(
            "Exactly 3 routers must be selected."
        )

    if len(set(selected_routers)) != 3:
        raise ValueError(
            "Router positions must be different."
        )

    if any(rid not in ROUTERS for rid in selected_routers):
        raise ValueError("Invalid router position.")

    covered = []
    uncovered = []

    for cid, classroom in CLASSROOMS.items():
        is_any_covered = False

        for rid in selected_routers:
            if verify_student_pair(
                classroom, ROUTERS[rid]
            ):
                is_any_covered = True
                break

        if is_any_covered:
            covered.append(cid)
        else:
            uncovered.append(cid)

    return {
        "covered": covered,
        "uncovered": uncovered,
        "count": len(covered),
        "rate": len(covered) / len(CLASSROOMS) * 100
    }


# =====================================================
# 4. GUI configuration
# =====================================================

root = tk.Tk()
root.title("INT6064 - Campus Wi-Fi Coding Lab")
root.geometry("1250x850")
root.minsize(1100, 750)

selected = []
result = None
tests_passed = False
verified_expressions = None

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

ttk.Label(
    main,
    text="Campus Wi-Fi Coding Lab",
    font=("Arial", 20, "bold")
).pack(anchor="w", pady=(0, 8))

content = ttk.Frame(main)
content.pack(fill="both", expand=True)

left = ttk.LabelFrame(
    content,
    text="2D Campus Map",
    padding=8
)
left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)

right = ttk.LabelFrame(
    content,
    text="Python Coding Exercise",
    padding=12
)
right.pack(
    side="right",
    fill="both",
    expand=True
)

CELL = 46
LEFT = 45
TOP = 45
BOTTOM = TOP + 9 * CELL

canvas = tk.Canvas(
    left,
    width=510,
    height=510,
    bg="white"
)
canvas.pack(pady=8)

selection_label = ttk.Label(
    left,
    text="Selected routers: None (0/3)"
)
selection_label.pack(pady=4)

status_label = ttk.Label(
    left,
    text="Stage 1: Complete coding tests",
    foreground="#a65e00",
    font=("Arial", 10, "bold")
)
status_label.pack(pady=5)


# =====================================================
# 5. Map
# =====================================================

def to_screen(x, y):
    return LEFT + x * CELL, BOTTOM - y * CELL


def draw_map():
    canvas.delete("all")

    for i in range(10):
        x = LEFT + i * CELL
        y = TOP + i * CELL

        canvas.create_line(
            x, TOP, x, BOTTOM,
            fill="#dddddd"
        )
        canvas.create_line(
            LEFT, y, LEFT + 9 * CELL, y,
            fill="#dddddd"
        )

        canvas.create_text(
            x, BOTTOM + 16, text=str(i)
        )
        canvas.create_text(
            LEFT - 17,
            BOTTOM - i * CELL,
            text=str(i)
        )

    # Coverage circle boundaries
    for rid in selected:
        rx, ry = ROUTERS[rid]
        previous = None

        for angle in range(361):
            theta = math.radians(angle)

            px = (
                rx + COVERAGE_RADIUS * math.cos(theta)
            )
            py = (
                ry + COVERAGE_RADIUS * math.sin(theta)
            )

            if 0 <= px <= 9 and 0 <= py <= 9:
                current = to_screen(px, py)

                if previous is not None:
                    canvas.create_line(
                        *previous,
                        *current,
                        fill="#31a66a",
                        width=2
                    )

                previous = current
            else:
                previous = None

    covered_set = (
        set(result["covered"]) if result else set()
    )

    # Classrooms
    for cid, pos in CLASSROOMS.items():
        x, y = to_screen(*pos)

        if result is None:
            color = "#468bd1"
        elif cid in covered_set:
            color = "#30a46c"
        else:
            color = "#df5353"

        canvas.create_oval(
            x-9, y-9, x+9, y+9,
            fill=color,
            outline="white"
        )

        canvas.create_text(
            x, y-18,
            text=cid,
            font=("Arial", 9)
        )

    # Router positions
    for rid, pos in ROUTERS.items():
        x, y = to_screen(*pos)

        color = (
            "#148452"
            if rid in selected
            else "#e6a038"
        )

        tags = ("router", f"router_{rid}")

        canvas.create_rectangle(
            x-12, y-12, x+12, y+12,
            fill=color,
            outline="#333333",
            tags=tags
        )

        canvas.create_text(
            x, y,
            text=rid,
            fill="white",
            font=("Arial", 10, "bold"),
            tags=tags
        )

    canvas.tag_bind(
        "router",
        "<Button-1>",
        click_router
    )


def click_router(event):
    items = canvas.find_overlapping(
        event.x, event.y, event.x, event.y
    )

    for item in reversed(items):
        for tag in canvas.gettags(item):
            if tag.startswith("router_"):
                toggle_router(tag.split("_", 1)[1])
                return


def update_selection_label():
    selection_label.config(
        text=(
            f"Selected routers: "
            f"{', '.join(selected) or 'None'} "
            f"({len(selected)}/3)"
        )
    )


def toggle_router(rid):
    global result

    if not tests_passed:
        messagebox.showinfo(
            "Coding First",
            "Complete all coding tests before "
            "selecting router positions."
        )
        return

    if get_expressions() != verified_expressions:
        invalidate_test()
        return

    if rid in selected:
        selected.remove(rid)
    elif len(selected) < 3:
        selected.append(rid)
    else:
        messagebox.showwarning(
            "Router Limit",
            "Select exactly 3 routers."
        )
        return

    update_selection_label()

    if len(selected) == 3:
        try:
            result = student_calculate(selected)
        except ValueError as error:
            invalidate_test()
            output.insert(
                "end",
                f"\nVerification failed: {error}\n"
            )
            return
    else:
        result = None

    update_results()
    draw_map()


# =====================================================
# 6. Code editors
# =====================================================

ttk.Label(
    right,
    text="TODO 1 - Calculate squared distance",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(4, 5))

ttk.Label(
    right,
    text="Use cx, cy, rx and ry."
).pack(anchor="w")

distance_editor = tk.Text(
    right,
    height=3,
    font=("Consolas", 12),
    bg="#202936",
    fg="white",
    insertbackground="white"
)
distance_editor.pack(fill="x", pady=8)

ttk.Label(
    right,
    text="TODO 2 - Check Wi-Fi coverage",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(10, 5))

ttk.Label(
    right,
    text="Use distance_squared and COVERAGE_RADIUS."
).pack(anchor="w")

condition_editor = tk.Text(
    right,
    height=3,
    font=("Consolas", 12),
    bg="#202936",
    fg="white",
    insertbackground="white"
)
condition_editor.pack(fill="x", pady=8)

ttk.Label(
    right,
    text=(
        "Enter expressions only. "
        "Do not include assignment or return."
    ),
    foreground="#666666"
).pack(anchor="w", pady=4)


# =====================================================
# 7. Independent tests
# =====================================================

DISTANCE_CASES = [
    ((2, 4), (2, 2), 4),
    ((3, 8), (6, 8), 9),
    ((1, 3), (4, 4), 10),
    ((6, 9), (8, 1), 68),
    ((4, 4), (4, 4), 0),
    ((1, 1), (4, 5), 25),
]

CONDITION_CASES = [
    (0, True),
    (4, True),
    (8, True),
    (9, True),
    (10, False),
    (16, False),
    (25, False),
    (100, False),
]

INTEGRATION_CASES = [
    ("Boundary C6-D", "C6", "D", True),
    ("Outside C3-G", "C3", "G", False),
    ("Inside C1-E", "C1", "E", True),
    ("Outside C2-B", "C2", "B", False),
]


def run_tests():
    global result, tests_passed, verified_expressions

    tests_passed = False
    verified_expressions = None
    result = None

    output.delete("1.0", "end")

    passed = 0
    total = 0

    try:
        # TODO 1 independent tests
        output.insert(
            "end",
            "=== TODO 1: Distance Tests ===\n"
        )

        for classroom, router, expected in DISTANCE_CASES:
            total += 1

            actual = calculate_student_distance(
                classroom, router
            )

            if math.isclose(
                actual, expected,
                rel_tol=0,
                abs_tol=1e-9
            ):
                passed += 1
                output.insert(
                    "end",
                    f"PASS - Distance {classroom} to {router}\n"
                )
            else:
                output.insert(
                    "end",
                    f"FAIL - Distance {classroom} to {router}: "
                    f"expected {expected}, got {actual}\n"
                )

        # TODO 2 independent tests
        output.insert(
            "end",
            "\n=== TODO 2: Coverage Tests ===\n"
        )

        for distance_squared, expected in CONDITION_CASES:
            total += 1

            actual = calculate_student_condition(
                distance_squared
            )

            if actual == expected:
                passed += 1
                output.insert(
                    "end",
                    f"PASS - distance²={distance_squared}\n"
                )
            else:
                output.insert(
                    "end",
                    f"FAIL - distance²={distance_squared}: "
                    f"expected {expected}, got {actual}\n"
                )

        # Integration tests
        output.insert(
            "end",
            "\n=== Integration Tests ===\n"
        )

        for name, cid, rid, expected in INTEGRATION_CASES:
            total += 1

            actual = student_is_covered(
                CLASSROOMS[cid],
                ROUTERS[rid]
            )

            if actual == expected:
                passed += 1
                output.insert(
                    "end",
                    f"PASS - {name}\n"
                )
            else:
                output.insert(
                    "end",
                    f"FAIL - {name}\n"
                )

        # Check all classroom-router pairs independently
        output.insert(
            "end",
            "\n=== Full Pair Verification ===\n"
        )

        pair_passed = 0
        for classroom in CLASSROOMS.values():
            for router in ROUTERS.values():
                total += 1

                try:
                    verify_student_pair(classroom, router)
                    passed += 1
                    pair_passed += 1
                except ValueError:
                    pass

        pair_total = len(CLASSROOMS) * len(ROUTERS)

        output.insert(
            "end",
            f"Verified classroom-router pairs: "
            f"{pair_passed}/{pair_total}\n"
        )

        # Router combination tests
        output.insert(
            "end",
            "\n=== Router Combination Tests ===\n"
        )

        for name, routers, expected_count in [
            ("Combination 1", ["B", "D", "E"], 12),
            ("Combination 2", ["G", "D", "B"], 11)
        ]:
            total += 1

            try:
                calculated = student_calculate(routers)

                correct = (
                    calculated["count"] == expected_count
                )

                if name == "Combination 2":
                    correct = (
                        correct
                        and calculated["uncovered"] == ["C3"]
                    )

                if correct:
                    passed += 1
                    output.insert(
                        "end",
                        f"PASS - {name}\n"
                    )
                else:
                    output.insert(
                        "end",
                        f"FAIL - {name}\n"
                    )

            except ValueError:
                output.insert(
                    "end",
                    f"FAIL - {name}\n"
                )

        output.insert(
            "end",
            f"\nTotal tests passed: {passed}/{total}\n"
        )

        if passed == total:
            tests_passed = True
            verified_expressions = get_expressions()

            status_label.config(
                text="Stage 2: Optimization Challenge",
                foreground="#148452"
            )

            output.insert(
                "end",
                "\nALL TESTS PASSED!\n"
                "Optimization Challenge unlocked.\n"
                "Select exactly 3 routers on the map.\n"
            )

            if len(selected) == 3:
                result = student_calculate(selected)

        else:
            result = None

            status_label.config(
                text="Stage 1: Fix your Python code",
                foreground="#b33a3a"
            )

            output.insert(
                "end",
                "\nTEST FAILED: Please correct your code.\n"
            )

        update_results()
        draw_map()

    except (
        ValueError,
        SyntaxError,
        TypeError,
        OverflowError,
        ZeroDivisionError
    ) as error:

        result = None
        tests_passed = False
        verified_expressions = None

        status_label.config(
            text="Stage 1: Fix your Python code",
            foreground="#b33a3a"
        )

        update_results()
        draw_map()

        output.insert(
            "end",
            f"\nCODE ERROR: {error}\n"
        )


# =====================================================
# 8. Results and reset
# =====================================================

def update_results():
    if result is None:
        result_label.config(
            text="Coverage: Not calculated"
        )
        progress["value"] = 0

    else:
        result_label.config(
            text=(
                f"Covered: {result['count']}/12 | "
                f"Coverage: {result['rate']:.2f}% | "
                f"Uncovered: "
                f"{', '.join(result['uncovered']) or 'None'}"
            )
        )

        progress["value"] = result["rate"]


def reset_map():
    global result

    selected.clear()
    result = None

    update_selection_label()
    update_results()
    draw_map()


def invalidate_test(event=None):
    global result, tests_passed, verified_expressions

    if event is not None and verified_expressions == get_expressions():
        return  # Cursor movement is not a code edit.

    result = None
    tests_passed = False
    verified_expressions = None

    status_label.config(
        text="Stage 1: Complete coding tests",
        foreground="#a65e00"
    )

    update_results()
    draw_map()

    output.delete("1.0", "end")
    output.insert(
        "end",
        "Code changed. Please run the tests again.\n"
    )


# =====================================================
# 9. Buttons and feedback
# =====================================================

button_frame = ttk.Frame(right)
button_frame.pack(fill="x", pady=10)

ttk.Button(
    button_frame,
    text="Run & Test",
    command=run_tests
).pack(side="left", padx=5)

ttk.Button(
    button_frame,
    text="Reset Map",
    command=reset_map
).pack(side="left", padx=5)

ttk.Label(
    right,
    text="Test Feedback",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(10, 5))

output = tk.Text(
    right,
    height=12,
    font=("Consolas", 10),
    bg="#f5f5f5"
)
output.pack(fill="both", expand=True)

result_label = ttk.Label(
    left,
    text="Coverage: Not calculated",
    font=("Arial", 11, "bold"),
    wraplength=500
)
result_label.pack(pady=8)

progress = ttk.Progressbar(
    left,
    maximum=100,
    length=420
)
progress.pack(pady=8)

ttk.Label(
    left,
    text=(
        "Blue: Not calculated | Green: Covered | "
        "Red: Uncovered | Orange: Router"
    ),
    font=("Arial", 9)
).pack(pady=5)

distance_editor.bind(
    "<KeyRelease>",
    invalidate_test
)

condition_editor.bind(
    "<KeyRelease>",
    invalidate_test
)

draw_map()
root.mainloop()
