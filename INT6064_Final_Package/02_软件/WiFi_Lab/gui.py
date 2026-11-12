
import tkinter as tk
from tkinter import ttk, messagebox

from data import CLASSROOMS, ROUTERS, COVERAGE_RADIUS
from coverage import calculate_coverage, is_covered

CELL = 48
GRID = 10
LEFT = 65
TOP = 65
RIGHT = LEFT + 9 * CELL
BOTTOM = TOP + 9 * CELL

selected = []
result = None

root = tk.Tk()
root.title("INT6064 - Campus Wi-Fi Coverage Optimizer")
root.geometry("920x900")
root.minsize(760, 780)

title = ttk.Label(
    root,
    text="Campus Wi-Fi Coverage Optimizer",
    font=("Arial", 19, "bold")
)
title.pack(pady=(12, 4))

instruction = ttk.Label(
    root,
    text="Select exactly 3 router locations (A-G). Click a classroom to inspect distances."
)
instruction.pack(pady=4)

selection_label = ttk.Label(
    root,
    text="Selected routers: None (0/3)",
    font=("Arial", 11, "bold")
)
selection_label.pack(pady=4)

canvas = tk.Canvas(
    root,
    width=570,
    height=570,
    bg="white",
    highlightthickness=1,
    highlightbackground="#cccccc"
)
canvas.pack(pady=8)

def to_screen(x, y):
    return LEFT + x * CELL, BOTTOM - y * CELL


def draw_map():
    canvas.delete("all")

    # Draw coordinate grid
    for i in range(GRID):
        x = LEFT + i * CELL
        y = TOP + i * CELL

        canvas.create_line(
            x, TOP, x, BOTTOM,
            fill="#dddddd"
        )
        canvas.create_line(
            LEFT, y, RIGHT, y,
            fill="#dddddd"
        )

        canvas.create_text(
            x, BOTTOM + 18,
            text=str(i),
            fill="#666666"
        )
        canvas.create_text(
            LEFT - 18, BOTTOM - i * CELL,
            text=str(i),
            fill="#666666"
        )

    canvas.create_text(
        RIGHT + 25, BOTTOM + 18, text="X"
    )
    canvas.create_text(
        LEFT - 18, TOP - 22, text="Y"
    )

    # Clip coverage circles to map bounds
    # Canvas clipping is approximated with line segments.
    for router_id in selected:
        rx, ry = ROUTERS[router_id]
        radius = COVERAGE_RADIUS

        import math

        previous = None
        for angle in range(361):
            theta = math.radians(angle)
            px = rx + radius * math.cos(theta)
            py = ry + radius * math.sin(theta)

            if 0 <= px <= 9 and 0 <= py <= 9:
                current = to_screen(px, py)
                if previous is not None:
                    canvas.create_line(
                        *previous, *current,
                        fill="#31a66a",
                        width=2
                    )
                previous = current
            else:
                previous = None

    # Classroom points
    covered = set(result["covered"]) if result else set()

    for cid, pos in CLASSROOMS.items():
        x, y = to_screen(*pos)

        if result:
            color = "#30a46c" if cid in covered else "#df5353"
        else:
            color = "#468bd1"

        canvas.create_oval(
            x-10, y-10, x+10, y+10,
            fill=color, outline="white",
            width=2,
            tags=("classroom", f"classroom_{cid}")
        )
        canvas.create_text(
            x, y-19, text=cid,
            font=("Arial", 9),
            tags=("classroom", f"classroom_{cid}")
        )

    # Candidate router positions
    for rid, pos in ROUTERS.items():
        x, y = to_screen(*pos)

        color = "#148452" if rid in selected else "#e6a038"

        canvas.create_rectangle(
            x-12, y-12, x+12, y+12,
            fill=color,
            outline="#333333",
            width=1,
            tags=("router", f"router_{rid}")
        )
        canvas.create_text(
            x, y, text=rid,
            fill="white",
            font=("Arial", 10, "bold"),
            tags=("router", f"router_{rid}")
        )

    canvas.tag_bind("router", "<Button-1>", click_router)
    canvas.tag_bind("classroom", "<Button-1>", click_classroom)


def find_tag(event, prefix):
    items = canvas.find_overlapping(
        event.x, event.y, event.x, event.y
    )

    for item in reversed(items):
        for tag in canvas.gettags(item):
            if tag.startswith(prefix):
                return tag[len(prefix):]
    return None


def click_router(event):
    rid = find_tag(event, "router_")
    if rid:
        toggle_router(rid)


def toggle_router(rid):
    global result

    if rid in selected:
        selected.remove(rid)
    elif len(selected) < 3:
        selected.append(rid)
    else:
        messagebox.showwarning(
            "Selection limit",
            "You can select only 3 router locations."
        )
        return

    result = None
    selection_label.config(
        text=f"Selected routers: {', '.join(selected) or 'None'} ({len(selected)}/3)"
    )
    update_results()
    draw_map()


def click_classroom(event):
    cid = find_tag(event, "classroom_")
    if not cid:
        return

    if not selected:
        messagebox.showinfo(
            "Distance inspection",
            "Please select at least one router first."
        )
        return

    cx, cy = CLASSROOMS[cid]
    lines = [f"{cid} = ({cx}, {cy})", ""]

    for rid in selected:
        rx, ry = ROUTERS[rid]
        dx2 = (cx - rx) ** 2
        dy2 = (cy - ry) ** 2
        d2 = dx2 + dy2

        covered = is_covered(
            CLASSROOMS[cid], ROUTERS[rid]
        )

        lines.append(
            f"Router {rid} ({rx}, {ry}):\n"
            f"d² = ({cx}-{rx})² + ({cy}-{ry})²\n"
            f"   = {dx2} + {dy2} = {d2}\n"
            f"{'Covered' if covered else 'Not covered'} "
            f"(d² {'<=' if covered else '>'} 9)\n"
        )

    messagebox.showinfo(
        f"Distance inspection - {cid}",
        "\n".join(lines)
    )


def update_results():
    if result is None:
        coverage_text.config(
            text="Coverage: Not calculated"
        )
        uncovered_text.config(
            text="Uncovered classrooms: -"
        )
        progress["value"] = 0
    else:
        coverage_text.config(
            text=(
                f"Covered: {result['count']}/12 | "
                f"Coverage: {result['rate']:.2f}%"
            )
        )
        uncovered_text.config(
            text="Uncovered classrooms: "
            + (", ".join(result["uncovered"]) or "None")
        )
        progress["value"] = result["rate"]


def calculate():
    global result

    if len(selected) != 3:
        messagebox.showwarning(
            "Invalid selection",
            "Please select exactly 3 routers."
        )
        return

    result = calculate_coverage(selected)
    update_results()
    draw_map()


def reset():
    global result
    selected.clear()
    result = None

    selection_label.config(
        text="Selected routers: None (0/3)"
    )
    update_results()
    draw_map()


button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Calculate Coverage",
    command=calculate
).pack(side="left", padx=8)

ttk.Button(
    button_frame,
    text="Reset",
    command=reset
).pack(side="left", padx=8)

result_frame = ttk.LabelFrame(
    root, text="Coverage Results", padding=12
)
result_frame.pack(fill="x", padx=35, pady=8)

coverage_text = ttk.Label(
    result_frame,
    text="Coverage: Not calculated",
    font=("Arial", 12, "bold")
)
coverage_text.pack(pady=5)

progress = ttk.Progressbar(
    result_frame,
    orient="horizontal",
    mode="determinate",
    maximum=100,
    length=450
)
progress.pack(pady=8)

uncovered_text = ttk.Label(
    result_frame,
    text="Uncovered classrooms: -"
)
uncovered_text.pack(pady=5)

legend = ttk.Label(
    root,
    text=(
        "Blue: Not calculated  |  "
        "Green: Covered / Selected router  |  "
        "Red: Uncovered  |  Orange: Candidate router"
    ),
    font=("Arial", 9)
)
legend.pack(pady=8)

draw_map()
root.mainloop()
