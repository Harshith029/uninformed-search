"""
engine/node.py
Search tree node — state, parent, action, depth, cumulative cost.
"""

from __future__ import annotations
from typing import Any, List, Optional


class Node:
    __slots__ = ("state", "parent", "action", "depth", "cost")

    def __init__(self, state, parent=None, action=None, cost=0.0):
        self.state  = state
        self.parent = parent
        self.action = action
        self.depth  = 0 if parent is None else parent.depth + 1
        self.cost   = cost

    def path_states(self) -> list:
        chain, node = [], self
        while node:
            chain.append(node.state)
            node = node.parent
        return list(reversed(chain))

    def path_actions(self) -> list:
        chain, node = [], self
        while node.parent:
            chain.append(node.action)
            node = node.parent
        return list(reversed(chain))

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return f"Node(depth={self.depth}, cost={self.cost}, state={self.state!r})"
