"""
main.py — Entry point.

Uninformed Search Strategies — Terminal Implementation
Artificial Intelligence — Individual Assignment

Run:  python main.py
"""

import sys, os, time

# ── terminal helpers ──────────────────────────────────────────────────────────

class C:
    R="\033[0m"; B="\033[1m"; DM="\033[2m"; IT="\033[3m"
    RED="\033[31m"; GRN="\033[32m"; YLW="\033[33m"
    BLU="\033[34m"; MAG="\033[35m"; CYN="\033[36m"
    WHT="\033[37m"; GRY="\033[90m"

def co(col, t): return f"{col}{t}{C.R}"
def clr():      os.system("cls" if os.name == "nt" else "clear")
def line(ch="─", n=72, col=C.GRY): print(co(col, ch * n))
def pause(msg="  Press ENTER to continue…"): input(co(C.GRY, msg))
def ask(prompt, col=C.B+C.WHT):
    try:    return input(f"\n  {co(col,'▶')}  {prompt}  ").strip()
    except: print(); return "q"

# ── imports ───────────────────────────────────────────────────────────────────

from engine.strategies import bfs, dfs, dls, iddfs, ucs, bds, STRATEGIES
from engine.metrics    import Metrics
from compare.table     import print_table, print_analysis

from problems.water_jug    import WaterJugProblem, VARIANTS as WJ_VARIANTS
from problems.missionaries import MissionariesProblem
from problems.eight_queens import EightQueensProblem
from problems.tic_tac_toe  import TicTacToeProblem

# ── strategy runner ───────────────────────────────────────────────────────────

_RUNS = [
    ("BFS",   bfs,   {}),
    ("DFS",   dfs,   {}),
    ("DLS",   dls,   {"limit": 15}),
    ("IDDFS", iddfs, {"max_limit": 50}),
    ("UCS",   ucs,   {}),
    ("BDS",   bds,   {}),
]

def run_all(problem, dls_limit=15, iddfs_max=50):
    """Run all 6 strategies; return [(node, metrics), …]."""
    runs = [
        ("BFS",   bfs,   {}),
        ("DFS",   dfs,   {}),
        ("DLS",   dls,   {"limit": dls_limit}),
        ("IDDFS", iddfs, {"max_limit": iddfs_max}),
        ("UCS",   ucs,   {}),
        ("BDS",   bds,   {}),
    ]
    results = []
    for name, fn, kw in runs:
        print(f"    {co(C.YLW, f'{name:<6}')} running…", end="\r")
        node, m = fn(problem, **kw)
        m.strategy     = name
        m.problem_name = type(problem).__name__
        results.append((node, m))
        ok   = co(C.GRN, "✔ found   ") if m.found else co(C.RED, "✘ no solution")
        dep  = str(m.solution_depth) if m.found else "—"
        exp  = str(m.nodes_expanded)
        print(f"    {co(C.B+C.YLW, f'{name:<6}')}  {ok}  "
              f"depth={dep:<4}  expanded={exp:<6}  {m.elapsed_ms:.3f}ms      ")
    return results

# ── solution path display ─────────────────────────────────────────────────────

def show_solution(node, problem, strategy_name):
    clr()
    if node is None:
        print(co(C.RED, f"\n  {strategy_name} — no solution found."))
        pause()
        return

    states  = node.path_states()
    actions = node.path_actions()

    line("═", col=C.B+C.CYN)
    print(co(C.B+C.CYN,
        f"  {strategy_name} — Solution Path  "
        f"({len(actions)} step{'s' if len(actions) != 1 else ''}, "
        f"cost={int(node.cost)})"))
    line("═", col=C.B+C.CYN)

    for i, state in enumerate(states):
        print()
        if i == 0:
            print(co(C.GRY, "  ┌── Initial State " + "─"*40))
        else:
            lbl = problem.action_label(actions[i - 1])
            print(co(C.YLW, f"  ┌── Step {i}:  {lbl} " + "─" * max(0, 38 - len(lbl))))
        print()
        if hasattr(problem, "display_state"):
            for ln in problem.display_state(state).split("\n"):
                print(ln)
        else:
            print(f"  {state}")
        print()
        print(co(C.GRY, "  └" + "─"*57))

    print()
    a, b = (node.state if isinstance(node.state, tuple) else (node.state, None))[:2] \
           if isinstance(node.state, tuple) else (node.state, None)
    print(co(C.B+C.GRN,
        f"  ✔  Goal reached at depth {node.depth}, cost {int(node.cost)}."))
    print()
    pause()

# ── solution picker ───────────────────────────────────────────────────────────

def pick_solution(results, problem, problem_title):
    while True:
        clr()
        line("─", col=C.CYN)
        print(co(C.B+C.CYN, f"  {problem_title} — View Solution Path"))
        line("─", col=C.CYN)
        print()
        for i, (name, _, _) in enumerate(_RUNS, 1):
            m = next((m for _, m in results if m.strategy == name), None)
            if m:
                ok = co(C.GRN, "✔") if m.found else co(C.RED, "✘")
                dep = f"depth={m.solution_depth}" if m.found else "no solution"
                print(f"    {co(C.B+C.YLW, str(i))}.  {ok}  {name:<6}  {dep}")
        print(f"\n    {co(C.B+C.YLW,'A')}.  Show all solutions in sequence")
        print(f"    {co(C.B+C.YLW,'Q')}.  Back")
        print()

        ch = ask("Select strategy", col=C.YLW).upper()
        if ch == "Q":
            return
        elif ch == "A":
            for name, _, _ in _RUNS:
                node = next((n for n, m in results if m.strategy == name), None)
                show_solution(node, problem, name)
        elif ch.isdigit() and 1 <= int(ch) <= len(_RUNS):
            name = _RUNS[int(ch) - 1][0]
            node = next((n for n, m in results if m.strategy == name), None)
            show_solution(node, problem, name)
        else:
            print(co(C.YLW, "  Invalid.")); time.sleep(0.6)

# ── problem description boxes ─────────────────────────────────────────────────

def _desc_box(lines, col=C.GRY):
    w = max(len(l) for l in lines) + 4
    print(co(col, "  ┌" + "─"*w + "┐"))
    for l in lines:
        pad = w - len(l) - 2
        print(co(col, "  │  ") + l + " "*pad + co(col, "  │"))
    print(co(col, "  └" + "─"*w + "┘"))
    print()

# ══════════════════════════════════════════════════════════════════════════════
# Problem 1 — Water Jug
# ══════════════════════════════════════════════════════════════════════════════

def menu_water_jug():
    while True:
        clr()
        line("═", col=C.B+C.BLU)
        print(co(C.B+C.BLU, "  PROBLEM 1 — Milk & Water Jug"))
        line("═", col=C.B+C.BLU)
        print()
        _desc_box([
            "Two jugs with no measuring marks.",
            "Operations: fill, empty, pour A→B, pour B→A.",
            "Goal: measure exactly GOAL litres in either jug.",
        ], col=C.BLU)

        print(co(C.B, "  SELECT VARIANT\n"))
        variants = list(WJ_VARIANTS.items())
        for i, (name, (ca, cb, g)) in enumerate(variants, 1):
            print(f"    {co(C.B+C.YLW, str(i))}.  {name.capitalize():<10} "
                  f"Jug A: {ca}L  │  Jug B: {cb}L  │  Goal: {g}L")
        print(f"    {co(C.B+C.YLW,'4')}.  Custom  — enter your own sizes")
        print(f"    {co(C.B+C.YLW,'Q')}.  Back to main menu")
        print()

        ch = ask("Select", col=C.YLW).upper()

        if ch == "Q":
            return
        elif ch == "4":
            prob = _custom_jug()
            if prob: _run_water_jug(prob, "Custom")
        elif ch.isdigit() and 1 <= int(ch) <= 3:
            name, (ca, cb, g) = variants[int(ch) - 1]
            _run_water_jug(WaterJugProblem(ca, cb, g), name.capitalize())
        else:
            print(co(C.YLW, "  Invalid.")); time.sleep(0.6)


def _custom_jug():
    print()
    def get_int(p, lo=1, hi=20):
        while True:
            v = ask(p, col=C.YLW)
            if v.upper() == "Q": return None
            if v.isdigit() and lo <= int(v) <= hi: return int(v)
            print(co(C.RED, f"  Enter {lo}–{hi}."))
    ca = get_int("Jug A capacity (1–20):")
    if ca is None: return None
    cb = get_int("Jug B capacity (1–20):")
    if cb is None: return None
    g  = get_int(f"Goal (1–{max(ca,cb)}):", lo=1, hi=max(ca,cb))
    if g  is None: return None
    return WaterJugProblem(ca, cb, g)


def _run_water_jug(prob, label):
    clr()
    line("─", col=C.BLU)
    print(co(C.B+C.BLU,
        f"  Water Jug ({label})  "
        f"A={prob.cap_a}L  B={prob.cap_b}L  Goal={prob.goal}L"))
    line("─", col=C.BLU)
    print()
    results = run_all(prob, dls_limit=12, iddfs_max=20)
    print()
    print_table([m for _, m in results],
                f"Water Jug ({label}) — All Strategies")
    print_analysis([m for _, m in results])
    pick_solution(results, prob, f"Water Jug ({label})")


# ══════════════════════════════════════════════════════════════════════════════
# Problem 2 — Missionaries & Cannibals
# ══════════════════════════════════════════════════════════════════════════════

def menu_missionaries():
    clr()
    line("═", col=C.B+C.RED)
    print(co(C.B+C.RED, "  PROBLEM 2 — Missionaries & Cannibals"))
    line("═", col=C.B+C.RED)
    print()
    _desc_box([
        "3 missionaries + 3 cannibals must cross a river.",
        "Boat holds 1–2 people.  At least 1 person must cross.",
        "Cannibals must NEVER outnumber missionaries on either bank.",
        "Initial: (3M 3C | boat | )",
        "Goal   : (     | boat |  3M 3C)",
    ], col=C.RED)

    prob = MissionariesProblem()
    line("─", col=C.RED)
    print()
    results = run_all(prob, dls_limit=15, iddfs_max=20)
    print()
    print_table([m for _, m in results],
                "Missionaries & Cannibals — All Strategies")
    print_analysis([m for _, m in results])
    pick_solution(results, prob, "Missionaries & Cannibals")


# ══════════════════════════════════════════════════════════════════════════════
# Problem 3 — Eight Queens
# ══════════════════════════════════════════════════════════════════════════════

def menu_eight_queens():
    clr()
    line("═", col=C.B+C.MAG)
    print(co(C.B+C.MAG, "  PROBLEM 3 — Eight Queens"))
    line("═", col=C.B+C.MAG)
    print()
    _desc_box([
        "Place 8 queens on an 8×8 chessboard.",
        "No two queens may share a row, column, or diagonal.",
        "Formulation: one queen per column, placed left to right.",
        "BFS is impractical here — DFS finds a solution fastest.",
    ], col=C.MAG)

    prob = EightQueensProblem()
    line("─", col=C.MAG)
    print()

    # BFS/UCS are very slow for 8-queens — cap them
    _RUNS_EQ = [
        ("BFS",   bfs,   {}),
        ("DFS",   dfs,   {}),
        ("DLS",   dls,   {"limit": 8}),
        ("IDDFS", iddfs, {"max_limit": 8}),
        ("UCS",   ucs,   {}),
        ("BDS",   bds,   {}),
    ]
    results = []
    for name, fn, kw in _RUNS_EQ:
        print(f"    {co(C.YLW, f'{name:<6}')} running…", end="\r")
        try:
            node, m = fn(prob, **kw)
        except KeyboardInterrupt:
            print(f"\n    {co(C.YLW, name)} skipped (Ctrl+C)")
            m = Metrics(strategy=name, problem_name="EightQueens"); node = None
        m.strategy = name
        results.append((node, m))
        ok  = co(C.GRN, "✔ found   ") if m.found else co(C.RED, "✘ no solution")
        dep = str(m.solution_depth) if m.found else "—"
        print(f"    {co(C.B+C.YLW, f'{name:<6}')}  {ok}  "
              f"depth={dep:<4}  expanded={m.nodes_expanded:<6}  {m.elapsed_ms:.3f}ms      ")

    print()
    print_table([m for _, m in results], "Eight Queens — All Strategies")
    print_analysis([m for _, m in results])

    # Show board for DFS solution (fastest)
    dfs_node = next((n for n, m in results if m.strategy == "DFS" and m.found), None)
    if dfs_node:
        print(co(C.B+C.MAG, "\n  DFS Solution Board:\n"))
        print(prob.display_state(dfs_node.state))
        print()

    pick_solution(results, prob, "Eight Queens")


# ══════════════════════════════════════════════════════════════════════════════
# Problem 4 — Tic-Tac-Toe
# ══════════════════════════════════════════════════════════════════════════════

def menu_tictactoe():
    clr()
    line("═", col=C.B+C.GRN)
    print(co(C.B+C.GRN, "  PROBLEM 4 — Tic-Tac-Toe"))
    line("═", col=C.B+C.GRN)
    print()
    _desc_box([
        "Search for a winning move sequence for X from an empty board.",
        "X and O alternate. X moves first.",
        "Goal: X achieves 3-in-a-row (row, column, or diagonal).",
        "BFS finds the shortest (depth-5) winning sequence.",
        "DFS finds any win very quickly.",
    ], col=C.GRN)

    prob = TicTacToeProblem()
    line("─", col=C.GRN)
    print()
    results = run_all(prob, dls_limit=9, iddfs_max=9)
    print()
    print_table([m for _, m in results], "Tic-Tac-Toe — All Strategies")
    print_analysis([m for _, m in results])

    # Show BFS solution step-by-step inline
    bfs_node = next((n for n, m in results if m.strategy == "BFS" and m.found), None)
    if bfs_node:
        states  = bfs_node.path_states()
        actions = bfs_node.path_actions()
        print(co(C.B+C.GRN,
            f"\n  BFS Optimal Winning Path for X  ({len(actions)} moves):\n"))
        for i, state in enumerate(states):
            player = "X" if i % 2 == 1 else "O"
            if i == 0:
                print(co(C.GRY, "  ── Initial board ──────────────"))
            else:
                pos = actions[i - 1]
                r, c = divmod(pos, 3)
                mover = "X" if i % 2 == 1 else "O"
                print(co(C.YLW,
                    f"  ── Move {i}: {mover} plays {prob.action_label(pos)} ──"))
            print(prob.display_state(state))
            print()

    pick_solution(results, prob, "Tic-Tac-Toe")


# ══════════════════════════════════════════════════════════════════════════════
# Cross-problem comparison
# ══════════════════════════════════════════════════════════════════════════════

def menu_compare_all():
    clr()
    line("═", col=C.B+C.CYN)
    print(co(C.B+C.CYN, "  FULL COMPARISON — All Problems × All Strategies"))
    line("═", col=C.B+C.CYN)
    print()
    print(co(C.GRY, "  Running all 6 strategies on all 4 problems. This may take a moment.\n"))

    problems = [
        ("Water Jug (Classic)", WaterJugProblem(4,3,2),      {"dls_limit":12,"iddfs_max":20}),
        ("Missionaries",        MissionariesProblem(),         {"dls_limit":15,"iddfs_max":20}),
        ("Eight Queens",        EightQueensProblem(),          {"dls_limit":8, "iddfs_max":8}),
        ("Tic-Tac-Toe",         TicTacToeProblem(),            {"dls_limit":9, "iddfs_max":9}),
    ]

    all_results = {}
    for pname, prob, kw in problems:
        print(co(C.B+C.YLW, f"\n  ── {pname} ──"))
        results = run_all(prob, **kw)
        all_results[pname] = results

    print()
    line("═", col=C.CYN)
    print(co(C.B+C.CYN, "  RESULTS\n"))

    for pname, prob, _ in problems:
        results = all_results[pname]
        print_table([m for _, m in results], pname)
        print_analysis([m for _, m in results])

    pause()


# ══════════════════════════════════════════════════════════════════════════════
# Strategy theory reference
# ══════════════════════════════════════════════════════════════════════════════

def menu_theory():
    clr()
    line("═", col=C.B+C.YLW)
    print(co(C.B+C.YLW, "  STRATEGY REFERENCE GUIDE"))
    line("═", col=C.B+C.YLW)

    strategies = [
        ("BFS — Breadth-First Search", "BFS Family",
         ["Frontier: FIFO queue",
          "Explores all nodes at depth d before depth d+1",
          "Complete: Yes   Optimal: Yes (unit costs)",
          "Time: O(b^d)    Space: O(b^d)",
          "Best for: small spaces, shortest path required"]),

        ("DFS — Depth-First Search", "DFS Family",
         ["Frontier: LIFO stack",
          "Explores as deep as possible before backtracking",
          "Complete: Yes (finite graphs)   Optimal: No",
          "Time: O(b^m)    Space: O(b·m)   ← memory efficient",
          "Best for: large/deep spaces, any solution acceptable"]),

        ("DLS — Depth-Limited Search", "DFS variant",
         ["DFS with hard depth cutoff L",
          "Prevents infinite loops in cyclic spaces",
          "Complete: Only if solution depth ≤ L",
          "Time: O(b^L)    Space: O(b·L)",
          "Best for: when solution depth is approximately known"]),

        ("IDDFS — Iterative Deepening DFS", "DFS variant",
         ["Runs DLS at limits 0, 1, 2, … until found",
          "Combines DFS memory efficiency with BFS optimality",
          "Complete: Yes   Optimal: Yes (unit costs)",
          "Time: O(b^d)    Space: O(b·d)   ← best of both worlds",
          "Best for: general-purpose when depth unknown"]),

        ("UCS — Uniform-Cost Search", "BFS variant",
         ["Frontier: min-heap ordered by path cost",
          "Expands lowest-cost node first",
          "Complete: Yes   Optimal: Yes (non-negative costs)",
          "Time: O(b^(1+C*/ε))   Space: same",
          "Best for: non-uniform step costs; identical to BFS for unit costs"]),

        ("BDS — Bidirectional Search", "BFS variant",
         ["Two simultaneous BFS — forward and backward",
          "Stops when frontiers meet in the middle",
          "Complete: Yes   Optimal: Yes (unit costs)",
          "Time: O(b^(d/2))   Space: O(b^(d/2))   ← huge saving",
          "Best for: when goal state is concrete and reversible"]),
    ]

    for name, family, points in strategies:
        print()
        print(co(C.B+C.CYN, f"  {name}"))
        print(co(C.GRY,     f"  Family: {family}"))
        for p in points:
            print(co(C.WHT, f"    • {p}"))

    print()
    line(col=C.GRY)
    pause()


# ══════════════════════════════════════════════════════════════════════════════
# Main menu
# ══════════════════════════════════════════════════════════════════════════════

def banner():
    clr()
    line("═", col=C.B+C.CYN)
    print(co(C.B+C.CYN, "  UNINFORMED SEARCH STRATEGIES"))
    print(co(C.GRY,     "  BFS · DFS · DLS · IDDFS · UCS · BDS"))
    print(co(C.GRY,     "  Artificial Intelligence — Individual Assignment"))
    line("═", col=C.B+C.CYN)
    print()


def main():
    while True:
        banner()
        print(co(C.B, "  SELECT A PROBLEM\n"))
        menu = [
            ("1", "Milk & Water Jug Problem",      "3 variants + custom"),
            ("2", "Missionaries & Cannibals",       "classic river crossing"),
            ("3", "Eight Queens",                   "N=8 chessboard"),
            ("4", "Tic-Tac-Toe",                    "X wins from empty board"),
            ("5", "Compare All Problems",           "all strategies × all problems"),
            ("6", "Strategy Reference Guide",       "theory & complexity"),
            ("Q", "Quit",                           ""),
        ]
        for key, label, hint in menu:
            h = co(C.GRY, f"  — {hint}") if hint else ""
            print(f"    {co(C.B+C.YLW, f'[{key}]')}  {label}{h}")
        print()
        line(col=C.GRY)

        ch = ask("Select", col=C.B+C.WHT).upper()

        if   ch == "1": menu_water_jug()
        elif ch == "2": menu_missionaries()
        elif ch == "3": menu_eight_queens()
        elif ch == "4": menu_tictactoe()
        elif ch == "5": menu_compare_all()
        elif ch == "6": menu_theory()
        elif ch in ("Q","QUIT","EXIT"):
            clr(); banner()
            print(co(C.GRY, "  Goodbye.\n")); sys.exit(0)
        else:
            print(co(C.YLW, "  Invalid selection.")); time.sleep(0.7)


if __name__ == "__main__":
    main()
