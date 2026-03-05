"""
problems/water_jug.py
=====================
Milk & Water Jug Problem
Two jugs (A and B) with no measuring marks.
Goal: measure exactly GOAL litres in either jug using fill/empty/pour ops.

Three built-in variants:
    classic  — 4L + 3L  → goal 2L
    medium   — 5L + 3L  → goal 4L
    hard     — 8L + 5L  → goal 6L

State  : (a, b)   — current fill levels
Actions: fill_a, fill_b, empty_a, empty_b, pour_a→b, pour_b→a
Goal   : goal ∈ (a, b)
BDS    : supported via goal_state() + reverse operators
"""

from engine.problem import Problem

VARIANTS = {
    "classic": (4, 3, 2),
    "medium" : (5, 3, 4),
    "hard"   : (8, 5, 6),
}


class WaterJugProblem(Problem):

    def __init__(self, cap_a=4, cap_b=3, goal=2):
        self.cap_a = cap_a
        self.cap_b = cap_b
        self.goal  = goal

    def initial_state(self):
        return (0, 0)

    def goal_test(self, state):
        return self.goal in state

    def actions(self, state):
        a, b = state
        acts = []
        if a < self.cap_a:            acts.append("fill_a")
        if b < self.cap_b:            acts.append("fill_b")
        if a > 0:                     acts.append("empty_a")
        if b > 0:                     acts.append("empty_b")
        if a > 0 and b < self.cap_b:  acts.append("pour_a→b")
        if b > 0 and a < self.cap_a:  acts.append("pour_b→a")
        return acts

    def result(self, state, action):
        a, b = state
        if action == "fill_a":   return (self.cap_a, b)
        if action == "fill_b":   return (a, self.cap_b)
        if action == "empty_a":  return (0, b)
        if action == "empty_b":  return (a, 0)
        if action == "pour_a→b":
            pour = min(a, self.cap_b - b)
            return (a - pour, b + pour)
        if action == "pour_b→a":
            pour = min(b, self.cap_a - a)
            return (a + pour, b - pour)
        return state

    def action_label(self, action):
        return {
            "fill_a"  : f"Fill Jug A  (→{self.cap_a}L)",
            "fill_b"  : f"Fill Jug B  (→{self.cap_b}L)",
            "empty_a" : "Empty Jug A (→0L)",
            "empty_b" : "Empty Jug B (→0L)",
            "pour_a→b": "Pour A → B",
            "pour_b→a": "Pour B → A",
        }.get(action, action)

    # ── BDS support ───────────────────────────────────────────────────────────

    def goal_state(self):
        return (self.goal, 0)

    def reverse_actions(self, state):
        return self.actions(state)

    def reverse_result(self, state, action):
        return self.result(state, action)

    def supports_bds(self):
        return True

    # ── rich display ──────────────────────────────────────────────────────────

    def display_state(self, state):
        a, b = state
        filled_a = "█" * a + "░" * (self.cap_a - a)
        filled_b = "█" * b + "░" * (self.cap_b - b)
        tag_a = " ◄ GOAL!" if a == self.goal else ""
        tag_b = " ◄ GOAL!" if b == self.goal else ""
        w = max(self.cap_a, self.cap_b) + 2
        lines = [
            f"  ┌{'─'*w}┐  ┌{'─'*w}┐",
            f"  │ {filled_a:<{w-1}}│  │ {filled_b:<{w-1}}│",
            f"  │ {a}L / {self.cap_a}L{tag_a:<{w - len(f'{a}L / {self.cap_a}L')}}│  "
            f"│ {b}L / {self.cap_b}L{tag_b:<{w - len(f'{b}L / {self.cap_b}L')}}│",
            f"  └{'─'*w}┘  └{'─'*w}┘",
            f"     Jug A          Jug B",
        ]
        return "\n".join(lines)
