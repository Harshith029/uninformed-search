"""
compare/table.py
Renders comparison tables and analysis to the terminal.
"""

from typing import List
from engine.metrics import Metrics

COLS = [
    "Strategy", "Found", "Sol. Depth", "Sol. Cost",
    "Expanded", "Generated", "Max Frontier", "Max Depth", "Time (ms)"
]


def _widths(rows):
    w = {c: len(c) for c in COLS}
    for row in rows:
        for c in COLS:
            w[c] = max(w[c], len(str(row.get(c, ""))))
    return w


def print_table(metrics_list: List[Metrics], title: str = ""):
    if not metrics_list:
        return
    rows   = [m.row() for m in metrics_list]
    w      = _widths(rows)
    total  = sum(w.values()) + len(COLS) * 3 + 1

    if title:
        print(f"\n  ╔{'═'*(total)}╗")
        t = f"  {title}"
        print(f"  ║{t:<{total}}║")
        print(f"  ╚{'═'*(total)}╝")

    top = "  ┌─" + "─┬─".join("─"*w[c] for c in COLS) + "─┐"
    hdr = "  │ " + " │ ".join(f"{c:<{w[c]}}" for c in COLS) + " │"
    div = "  ├─" + "─┼─".join("─"*w[c] for c in COLS) + "─┤"
    bot = "  └─" + "─┴─".join("─"*w[c] for c in COLS) + "─┘"

    print(top); print(hdr); print(div)
    for row in rows:
        print("  │ " + " │ ".join(f"{str(row.get(c,'')):<{w[c]}}" for c in COLS) + " │")
    print(bot)
    print()


def print_analysis(metrics_list: List[Metrics]):
    solved = [m for m in metrics_list if m.found]
    print("  ── Performance Analysis " + "─" * 44)
    if not solved:
        print("  No strategy found a solution within limits.")
        print()
        return

    best_depth    = min(solved, key=lambda m: (m.solution_depth or 999))
    best_cost     = min(solved, key=lambda m: (m.solution_cost  or 999))
    fewest_exp    = min(solved, key=lambda m: m.nodes_expanded)
    fewest_gen    = min(solved, key=lambda m: m.nodes_generated)
    fastest       = min(solved, key=lambda m: m.elapsed_ms)
    smallest_mem  = min(solved, key=lambda m: m.max_frontier)

    def _row(label, m, detail):
        print(f"  {label:<22}  {m.strategy:<8}  {detail}")

    _row("Shallowest solution",  best_depth,   f"depth  = {best_depth.solution_depth}")
    _row("Lowest-cost solution", best_cost,    f"cost   = {best_cost.solution_cost}")
    _row("Fewest nodes expanded",fewest_exp,   f"expanded  = {fewest_exp.nodes_expanded}")
    _row("Fewest nodes generated",fewest_gen,  f"generated = {fewest_gen.nodes_generated}")
    _row("Smallest frontier",    smallest_mem, f"max frontier = {smallest_mem.max_frontier}")
    _row("Fastest wall time",    fastest,      f"time = {fastest.elapsed_ms:.3f} ms")
    print()
