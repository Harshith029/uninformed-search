"""
problems/missionaries.py
=========================
Missionaries and Cannibals Problem
3 missionaries + 3 cannibals must cross a river.
Boat holds 1–2 people.
Cannibals must never outnumber missionaries on either bank.

State  : (m_left, c_left, boat)
         m_left  = missionaries on left bank  (0–3)
         c_left  = cannibals    on left bank  (0–3)
         boat    = 'L' (left) | 'R' (right)

Initial: (3, 3, 'L')
Goal   : (0, 0, 'R')

BDS    : supported
"""

from engine.problem import Problem

M = 3   # total missionaries
C = 3   # total cannibals

# All possible boat loads (missionaries, cannibals)
_LOADS = [(1,0),(0,1),(1,1),(2,0),(0,2)]


class MissionariesProblem(Problem):

    def initial_state(self):
        return (M, C, 'L')

    def goal_test(self, state):
        return state == (0, 0, 'R')

    def _safe(self, ml, cl):
        """True if neither bank has cannibals outnumbering missionaries."""
        mr, cr = M - ml, C - cl
        if ml > 0 and cl > ml: return False
        if mr > 0 and cr > mr: return False
        return True

    def actions(self, state):
        ml, cl, boat = state
        valid = []
        for dm, dc in _LOADS:
            if boat == 'L':
                nm, nc = ml - dm, cl - dc
            else:
                nm, nc = ml + dm, cl + dc
            if 0 <= nm <= M and 0 <= nc <= C and self._safe(nm, nc):
                valid.append((dm, dc))
        return valid

    def result(self, state, action):
        ml, cl, boat = state
        dm, dc = action
        if boat == 'L':
            return (ml - dm, cl - dc, 'R')
        else:
            return (ml + dm, cl + dc, 'L')

    def action_label(self, action):
        dm, dc = action
        parts = ([f"{dm}M"] if dm else []) + ([f"{dc}C"] if dc else [])
        return "Move " + "+".join(parts)

    # ── BDS support ───────────────────────────────────────────────────────────

    def goal_state(self):
        return (0, 0, 'R')

    def reverse_actions(self, state):
        return self.actions(state)

    def reverse_result(self, state, action):
        return self.result(state, action)

    def supports_bds(self):
        return True

    # ── rich display ──────────────────────────────────────────────────────────

    def display_state(self, state):
        ml, cl, boat = state
        mr, cr = M - ml, C - cl

        m_l = "👤" * ml + "  " * (M - ml)
        c_l = "😈" * cl + "  " * (C - cl)
        m_r = "  " * (M - mr) + "👤" * mr
        c_r = "  " * (C - cr) + "😈" * cr

        boat_l = "⛵" if boat == 'L' else "  "
        boat_r = "  " if boat == 'L' else "⛵"

        return (
            f"  LEFT BANK            RIVER          RIGHT BANK\n"
            f"  M: {m_l}  {boat_l}  ≈≈≈≈≈≈≈≈  {boat_r}  {m_r} :M\n"
            f"  C: {c_l}             {c_r} :C\n"
            f"  [{ml}M {cl}C]                         [{mr}M {cr}C]"
        )
