"""Teacher reference view for the revised lab.

The student windows never show the optimal plan. This window is for the
teacher: it lists the three optima, the greedy walk and all 35 plans.

    python teacher_view.py
"""

import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "stage3"))

import tkinter as tk
from tkinter import ttk

from data import (  # noqa: E402
    CLASSROOMS, ROUTERS, ROUTER_COVERAGE,
    INSTALLATION_COSTS, ROUTER_LIMIT,
)

MAX_COST = max(
    sum(INSTALLATION_COSTS[r] for r in group)
    for group in combinations(sorted(ROUTERS), ROUTER_LIMIT)
)

WEIGHTS = [(1.0, "100/0"), (0.7, "70/30"), (0.3, "30/70")]


def score_plan(group, alpha):
    covered = set()
    for router in group:
        covered.update(set(ROUTER_COVERAGE[router]))
    cost = sum(INSTALLATION_COSTS[r] for r in group)
    q = len(covered) / len(CLASSROOMS)
    l = 1 - cost / MAX_COST
    return alpha * q + (1 - alpha) * l, len(covered), cost, covered


def best_for(alpha):
    rows = []
    for group in combinations(sorted(ROUTERS), ROUTER_LIMIT):
        s, n, c, cov = score_plan(group, alpha)
        rows.append((s, n, c, cov, group))
    rows.sort(key=lambda r: (-r[0], r[2], r[4]))
    return rows[0]


def greedy_trace():
    chosen, covered, lines = [], set(), []
    while len(chosen) < ROUTER_LIMIT:
        best, best_gain = None, -1
        for rid in sorted(ROUTERS):
            if rid in chosen:
                continue
            gain = len(set(ROUTER_COVERAGE[rid]) - covered)
            if gain > best_gain:
                best, best_gain = rid, gain
        chosen.append(best)
        covered |= set(ROUTER_COVERAGE[best])
        lines.append(f"round {len(chosen)}: {best} (+{best_gain})  total {len(covered)}/12")
    return chosen, lines


def build_text():
    out = []
    out.append("TEACHER REFERENCE  (students never see this window)")
    out.append("=" * 58)
    out.append(f"Kmax = {MAX_COST}   classrooms = {len(CLASSROOMS)}   positions = {len(ROUTERS)}")
    out.append("")
    out.append("Best plan under each weighting")
    out.append("-" * 58)
    for alpha, label in WEIGHTS:
        s, n, c, cov, group = best_for(alpha)
        missed = [cid for cid in CLASSROOMS if cid not in cov]
        out.append(
            f"  {label:>6}  {'+'.join(group):<6} {n}/12  cost {c:<5} "
            f"score {s:.4f}  missed {', '.join(missed) or '-'}"
        )

    chosen, lines = greedy_trace()
    out.append("")
    out.append("Greedy walk (coverage only)")
    out.append("-" * 58)
    for line in lines:
        out.append("  " + line)
    out.append(f"  result {'+'.join(chosen)}   (coverage optimum is B+D+E, 12/12)")

    out.append("")
    out.append("All 35 plans, scored at 70/30")
    out.append("-" * 58)
    out.append(f"  {'plan':<8}{'cover':>6}{'cost':>7}{'score':>9}  missed")
    rows = []
    for group in combinations(sorted(ROUTERS), ROUTER_LIMIT):
        s, n, c, cov = score_plan(group, 0.7)
        rows.append((s, n, c, cov, group))
    rows.sort(key=lambda r: (-r[0], r[2], r[4]))
    for s, n, c, cov, group in rows:
        missed = [cid for cid in CLASSROOMS if cid not in cov]
        out.append(
            f"  {'+'.join(group):<8}{n:>4}/12{c:>7}{s:>9.4f}  {', '.join(missed) or '-'}"
        )
    return "\n".join(out)


def main():
    root = tk.Tk()
    root.title("Teacher reference | Campus Wi-Fi Lab")
    root.geometry("720x760")

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Teacher reference — three optima, greedy walk, all 35 plans",
        font=("Arial", 12, "bold"),
    ).pack(anchor="w", pady=(0, 8))

    box = tk.Text(frame, font=("Consolas", 9), wrap="none")
    box.pack(fill="both", expand=True)
    box.insert("1.0", build_text())
    box.configure(state="disabled")

    root.mainloop()


if __name__ == "__main__":
    main()
