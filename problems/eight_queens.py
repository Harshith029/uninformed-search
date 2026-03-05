"""
problems/eight_queens.py
=========================
Eight Queens Problem
Place 8 queens on an 8×8 board so that no two attack each other
(no shared row, column, or diagonal).

Formulation: place queens column by column.
State  : tuple of length k (0 ≤ k ≤ 8); state[col] = row of queen in that col.
         Partial placement — column conflicts are impossible by construction.
Initial: ()
Goal   : len(state) == 8
Actions: valid row numbers for the next column

N can be changed at the top for smaller/larger boards.
"""

from engine.problem import Problem

N = 8   # board size


class EightQueensProblem(Problem):

    def initial_state(self):
        return ()

    def goal_test(self, state):
        return len(state) == N

    def actions(self, state):
        col = len(state)
        if col >= N:
            return []
        return [row for row in range(N) if self._no_conflict(state, col, row)]

    def _no_conflict(self, state, col, row):
        for c, r in enumerate(state):
            if r == row:                       return False   # same row
            if abs(r - row) == abs(c - col):   return False   # diagonal
        return True

    def result(self, state, action):
        return state + (action,)

    def action_label(self, action):
        return f"Row {action + 1}"

    # ── BDS not applicable (no meaningful reverse for partial placements)

    def supports_bds(self):
        return False

    # ── rich display ──────────────────────────────────────────────────────────

    def display_state(self, state):
        COL_LABELS = "ABCDEFGH"[:N]
        lines = []
        for row in range(N):
            rank = N - row
            line = f"  {rank} "
            for col in range(N):
                if col < len(state) and state[col] == row:
                    line += " Q "
                else:
                    line += "░░░" if (row + col) % 2 == 0 else "▓▓▓"
            lines.append(line)
        lines.append("    " + "".join(f" {c} " for c in COL_LABELS))
        if len(state) == N:
            positions = ", ".join(
                f"{COL_LABELS[c]}{N - state[c]}" for c in range(N)
            )
            lines.append(f"\n  Queens at: {positions}")
        return "\n".join(lines)
