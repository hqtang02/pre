"""Teacher demo: classroom distances, all 35 plans, greedy walk.

Read-only classroom tool. It never changes the student windows and it
reads its data from stage3/data.py, so costs and coverage stay in sync
with the lab.

    python teacher_demo.py      (or Start_Teacher_Demo.bat)
"""

import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "stage3"))

import tkinter as tk
from tkinter import ttk

from data import (  # noqa: E402
    CLASSROOMS,
    ROUTERS,
    ROUTER_COVERAGE,
    INSTALLATION_COSTS,
    ROUTER_LIMIT,
)

GRID = 10
CELL = 46
LEFT = 45
TOP = 45
BOTTOM = TOP + (GRID - 1) * CELL

MAX_COST = max(
    sum(INSTALLATION_COSTS[r] for r in group)
    for group in combinations(sorted(ROUTERS), ROUTER_LIMIT)
)

WEIGHTS = [("100/0  覆盖优先", 1.0), ("70/30  综合考虑", 0.7), ("30/70  成本优先", 0.3)]


def to_screen(x, y):
    return LEFT + x * CELL, BOTTOM - y * CELL


def score_of(group, alpha):
    covered = set()
    for router in group:
        covered.update(set(ROUTER_COVERAGE[router]))
    cost = sum(INSTALLATION_COSTS[r] for r in group)
    q = len(covered) / len(CLASSROOMS)
    l = 1 - cost / MAX_COST
    return alpha * q + (1 - alpha) * l, covered, cost


def current_alpha():
    return WEIGHTS[weight_box.current()][1]


class TeacherDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teacher demo | Campus Wi-Fi Lab")
        self.geometry("980x700")
        self.selected = []
        self.current_best = None

        left = ttk.Frame(self, padding=8)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(self, padding=10)
        right.pack(side="right", fill="both")

        self.canvas = tk.Canvas(left, width=520, height=520, bg="white")
        self.canvas.pack()
        self.hint = ttk.Label(
            left,
            text="Click a square to select a position (exactly 3). Click a classroom to inspect distances.",
            wraplength=500,
        )
        self.hint.pack(anchor="w", pady=6)

        ttk.Label(right, text="Scoring", font=("Arial", 11, "bold")).pack(anchor="w")
        global weight_box
        weight_box = ttk.Combobox(
            right, values=[w[0] for w in WEIGHTS], state="readonly", width=20
        )
        weight_box.current(1)
        weight_box.pack(anchor="w", pady=(2, 8))
        weight_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.best_label = ttk.Label(right, text="", wraplength=300, justify="left")
        self.best_label.pack(anchor="w", pady=4)

        self.result_label = ttk.Label(right, text="", wraplength=300, justify="left")
        self.result_label.pack(anchor="w", pady=4)

        self.distance_label = ttk.Label(right, text="", wraplength=300, justify="left")
        self.distance_label.pack(anchor="w", pady=4)

        ttk.Button(right, text="All 35 plans", command=self.show_all).pack(fill="x", pady=3)
        ttk.Button(right, text="Greedy walk", command=self.show_greedy).pack(fill="x", pady=3)
        ttk.Button(right, text="Clear selection", command=self.clear).pack(fill="x", pady=3)

        ttk.Label(
            right,
            text=f"Kmax = {MAX_COST} (highest cost of any three positions)\n"
                 "Costs: " + ", ".join(f"{r} {INSTALLATION_COSTS[r]}" for r in sorted(ROUTERS)),
            wraplength=300, justify="left", font=("Arial", 8),
        ).pack(anchor="w", pady=(10, 0))

        self.draw()
        self.refresh()

    # ---------------------------------------------------------------- drawing
    def draw(self):
        c = self.canvas
        c.delete("all")
        half = CELL / 2
        for i in range(GRID + 1):
            x = LEFT - half + i * CELL
            c.create_line(x, TOP - half, x, BOTTOM + half, fill="#dddddd")
            c.create_line(LEFT - half, TOP - half + i * CELL,
                          LEFT + (GRID - 1) * CELL + half, TOP - half + i * CELL,
                          fill="#dddddd")
        for i in range(GRID):
            c.create_text(LEFT + i * CELL, BOTTOM + half + 12, text=str(i))
            c.create_text(LEFT - half - 12, BOTTOM - i * CELL, text=str(i))

        for cid, pos in CLASSROOMS.items():
            x, y = to_screen(*pos)
            c.create_oval(x - 9, y - 9, x + 9, y + 9, fill="#468bd1", outline="white",
                          tags=("classroom", cid))
            c.create_text(x, y - 18, text=cid, font=("Arial", 8))
            c.tag_bind(cid, "<Button-1>", lambda e, name=cid: self.inspect(name))

        for rid, pos in ROUTERS.items():
            x, y = to_screen(*pos)
            color = "#148452" if rid in self.selected else "#e6a038"
            c.create_rectangle(x - 12, y - 12, x + 12, y + 12,
                               fill=color, outline="#333333", tags=("router", rid))
            c.create_text(x, y, text=rid, fill="white", font=("Arial", 10, "bold"))
            c.create_text(x, y + 20, text=str(INSTALLATION_COSTS[rid]),
                          fill="#6d4c41", font=("Arial", 8, "bold"))
            c.tag_bind(rid, "<Button-1>", lambda e, name=rid: self.toggle(name))

    # ---------------------------------------------------------------- state
    def toggle(self, rid):
        if rid in self.selected:
            self.selected.remove(rid)
        elif len(self.selected) < ROUTER_LIMIT:
            self.selected.append(rid)
        self.draw()
        self.refresh()

    def clear(self):
        self.selected.clear()
        self.draw()
        self.refresh()

    def refresh(self):
        alpha = current_alpha()
        best = max(
            combinations(sorted(ROUTERS), ROUTER_LIMIT),
            key=lambda g: (score_of(g, alpha)[0], -sum(INSTALLATION_COSTS[r] for r in g)),
        )
        s, cov, cost = score_of(best, alpha)
        missed = [c for c in CLASSROOMS if c not in cov]
        self.current_best = best
        self.best_label.config(
            text=(f"Best at {WEIGHTS[weight_box.current()][0]}:\n"
                  f"{'+'.join(best)}   {len(cov)}/12   cost {cost}   score {s:.4f}\n"
                  f"misses {', '.join(missed) or 'none'}")
        )

        if len(self.selected) == ROUTER_LIMIT:
            s2, cov2, cost2 = score_of(self.selected, alpha)
            missed2 = [c for c in CLASSROOMS if c not in cov2]
            self.result_label.config(
                text=(f"Your selection {'+'.join(sorted(self.selected))}:\n"
                      f"{len(cov2)}/12   cost {cost2}   score {s2:.4f}\n"
                      f"misses {', '.join(missed2) or 'none'}")
            )
        else:
            self.result_label.config(text=f"Selected {len(self.selected)}/3")

        self.distance_label.config(text="")

    def inspect(self, cid):
        cx, cy = CLASSROOMS[cid]
        lines = [f"{cid} ({cx},{cy})"]
        for rid in sorted(ROUTERS):
            rx, ry = ROUTERS[rid]
            d2 = (cx - rx) ** 2 + (cy - ry) ** 2
            mark = "covered" if d2 <= 9 else ""
            lines.append(f"  {rid}: d² = {d2} {mark}")
        self.distance_label.config(text="\n".join(lines))

    # ---------------------------------------------------------------- reports
    def show_all(self):
        alpha = current_alpha()
        rows = []
        for group in combinations(sorted(ROUTERS), ROUTER_LIMIT):
            s, cov, cost = score_of(group, alpha)
            rows.append((s, len(cov), cost, group, cov))
        rows.sort(key=lambda r: (-r[0], r[2], r[3]))
        lines = [f"All 35 plans at {WEIGHTS[weight_box.current()][0]}", ""]
        for s, n, cost, group, cov in rows:
            missed = [c for c in CLASSROOMS if c not in cov]
            lines.append(f"{'+'.join(group):<8}{n:>2}/12  cost {cost:<5} score {s:.4f}  "
                         f"misses {', '.join(missed) or '-'}")
        self._window("All 35 plans", lines)

    def show_greedy(self):
        chosen, covered, lines = [], set(), []
        while len(chosen) < ROUTER_LIMIT:
            best, gain = None, -1
            for rid in sorted(ROUTERS):
                if rid in chosen:
                    continue
                g = len(set(ROUTER_COVERAGE[rid]) - covered)
                if g > gain:
                    best, gain = rid, g
            chosen.append(best)
            covered |= set(ROUTER_COVERAGE[best])
            lines.append(f"round {len(chosen)}: {best}  +{gain}   total {len(covered)}/12")
        s, cov, cost = score_of(chosen, current_alpha())
        lines.append("")
        lines.append(f"result {'+'.join(chosen)}  {len(cov)}/12  cost {cost}  score {s:.4f}")
        lines.append("coverage optimum is B+D+E (12/12); at 70/30 the same set also wins")
        self._window("Greedy walk", lines)

    def _window(self, title, lines):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("620x560")
        text = tk.Text(win, font=("Consolas", 9))
        text.pack(fill="both", expand=True)
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")


if __name__ == "__main__":
    TeacherDemo().mainloop()
