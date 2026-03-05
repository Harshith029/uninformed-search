"""
problems/tic_tac_toe.py
=======================
Tic-Tac-Toe Search Problem
Search for a winning move sequence for X starting from an empty board.
X and O alternate. X moves first. Goal: X achieves three-in-a-row.

State  : 9-tuple of ' ', 'X', 'O'  (row-major, positions 0–8)
Initial: (' ',' ',' ',' ',' ',' ',' ',' ',' ')
Actions: index of any empty cell (0–8)
Goal   : X has three in a row, column, or diagonal

       0 | 1 | 2
       ---------
       3 | 4 | 5
       ---------
       6 | 7 | 8
"""

from engine.problem import Problem

_WINS = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # columns
    (0,4,8),(2,4,6),           # diagonals
]

EMPTY = tuple([' '] * 9)


def _winner(board):
    for a, b, c in _WINS:
        if board[a] == board[b] == board[c] != ' ':
            return board[a]
    return None


def _whose_turn(board):
    xs = board.count('X')
    os = board.count('O')
    return 'X' if xs == os else 'O'


class TicTacToeProblem(Problem):

    def initial_state(self):
        return EMPTY

    def goal_test(self, state):
        return _winner(state) == 'X'

    def actions(self, state):
        if _winner(state):   # game already over
            return []
        if ' ' not in state: # draw
            return []
        return [i for i, v in enumerate(state) if v == ' ']

    def result(self, state, action):
        board       = list(state)
        board[action] = _whose_turn(state)
        return tuple(board)

    def action_label(self, action):
        row, col = divmod(action, 3)
        return f"({row+1},{col+1})"

    # ── BDS not practical (too many possible goal boards)

    def supports_bds(self):
        return False

    # ── rich display ──────────────────────────────────────────────────────────

    def display_state(self, state):
        def cell(i):
            v = state[i]
            if v == 'X': return ' X '
            if v == 'O': return ' O '
            return f' {i} '   # show index for empty cells

        rows = []
        for r in range(3):
            base = r * 3
            rows.append("  " + "|".join(cell(base + c) for c in range(3)))
            if r < 2:
                rows.append("  ---+---+---")

        w = _winner(state)
        if w:
            rows.append(f"\n  ★ {w} wins!")
        elif ' ' not in state:
            rows.append("\n  Draw.")
        return "\n".join(rows)
