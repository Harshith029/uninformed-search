"""
engine/strategies.py
===================================================================
Six uninformed (blind) search strategies.

BFS Family                  DFS Family
──────────────────────      ──────────────────────────────────────
BFS  Breadth-First          DFS  Depth-First
UCS  Uniform-Cost           DLS  Depth-Limited   (DFS + limit)
BDS  Bidirectional          IDDFS Iterative Deepening (DFS + BFS)
===================================================================

Every function has signature:
    strategy_fn(problem, **kwargs) -> (Node | None, Metrics)
"""

from __future__ import annotations
import heapq
from collections import deque
from engine.node    import Node
from engine.problem import Problem
from engine.metrics import Metrics

# Sentinel returned by DLS when limit is hit without finding goal
_CUTOFF = object()

# ── shared helper ─────────────────────────────────────────────────────────────

def _child_nodes(node: Node, problem: Problem, m: Metrics):
    """Generate all child nodes from node, updating metrics."""
    for action in problem.actions(node.state):
        s2   = problem.result(node.state, action)
        cost = node.cost + problem.step_cost(node.state, action)
        child = Node(s2, node, action, cost)
        m.nodes_generated  += 1
        m.max_depth_seen    = max(m.max_depth_seen, child.depth)
        yield child


# ══════════════════════════════════════════════════════════════════════════════
# 1. BFS — Breadth-First Search
# ══════════════════════════════════════════════════════════════════════════════

def bfs(problem: Problem, **_):
    """
    FIFO queue — explore shallowest nodes first.
    Guarantees shortest path (fewest steps) for unit-cost problems.

    Complexity — Time: O(b^d)   Space: O(b^d)
    """
    m = Metrics(strategy="BFS", problem_name=type(problem).__name__)
    m.start()

    root = Node(problem.initial_state())
    if problem.goal_test(root.state):
        m.found = True; m.solution_depth = 0; m.solution_cost = 0
        m.stop(); return root, m

    frontier  = deque([root])
    explored  = {root.state}

    while frontier:
        m.max_frontier = max(m.max_frontier, len(frontier))
        node = frontier.popleft()
        m.nodes_expanded += 1

        for child in _child_nodes(node, problem, m):
            if child.state in explored:
                continue
            if problem.goal_test(child.state):
                m.found = True
                m.solution_depth = child.depth
                m.solution_cost  = child.cost
                m.stop(); return child, m
            explored.add(child.state)
            frontier.append(child)

    m.stop(); return None, m


# ══════════════════════════════════════════════════════════════════════════════
# 2. DFS — Depth-First Search
# ══════════════════════════════════════════════════════════════════════════════

def dfs(problem: Problem, max_depth: int = 1000, **_):
    """
    LIFO stack — explore deepest nodes first.
    Memory-efficient; may find non-optimal solutions.

    Complexity — Time: O(b^m)   Space: O(b·m)
    """
    m = Metrics(strategy="DFS", problem_name=type(problem).__name__)
    m.start()

    frontier = [Node(problem.initial_state())]
    explored = set()

    while frontier:
        m.max_frontier = max(m.max_frontier, len(frontier))
        node = frontier.pop()

        if node.state in explored:
            continue
        explored.add(node.state)
        m.nodes_expanded += 1

        if problem.goal_test(node.state):
            m.found = True
            m.solution_depth = node.depth
            m.solution_cost  = node.cost
            m.stop(); return node, m

        if node.depth < max_depth:
            # push in reverse so leftmost child is explored first
            for child in reversed(list(_child_nodes(node, problem, m))):
                if child.state not in explored:
                    frontier.append(child)

    m.stop(); return None, m


# ══════════════════════════════════════════════════════════════════════════════
# 3. DLS — Depth-Limited Search  (DFS variant)
# ══════════════════════════════════════════════════════════════════════════════

def dls(problem: Problem, limit: int = 10, **_):
    """
    DFS with a hard depth cutoff.
    Avoids infinite loops in cyclic state spaces.
    Returns None if no solution found within limit.

    Complexity — Time: O(b^l)   Space: O(b·l)
    """
    m = Metrics(strategy=f"DLS(L={limit})", problem_name=type(problem).__name__)
    m.start()

    result = _dls_rec(Node(problem.initial_state()), problem, limit, set(), m)

    if isinstance(result, Node):
        m.found = True
        m.solution_depth = result.depth
        m.solution_cost  = result.cost
        m.stop(); return result, m

    m.stop(); return None, m


def _dls_rec(node, problem, limit, visited, m):
    if problem.goal_test(node.state):
        return node
    if limit == 0:
        return _CUTOFF

    visited = visited | {node.state}
    m.nodes_expanded += 1
    cutoff_hit = False

    for child in _child_nodes(node, problem, m):
        if child.state in visited:
            continue
        result = _dls_rec(child, problem, limit - 1, visited, m)
        if result is _CUTOFF:
            cutoff_hit = True
        elif result is not None:
            return result

    return _CUTOFF if cutoff_hit else None


# ══════════════════════════════════════════════════════════════════════════════
# 4. IDDFS — Iterative Deepening DFS  (DFS variant)
# ══════════════════════════════════════════════════════════════════════════════

def iddfs(problem: Problem, max_limit: int = 50, **_):
    """
    Runs DLS at limits 0, 1, 2, … until a solution is found.
    Optimal like BFS, memory-efficient like DFS.
    Best general-purpose uninformed strategy.

    Complexity — Time: O(b^d)   Space: O(b·d)
    """
    m = Metrics(strategy="IDDFS", problem_name=type(problem).__name__)
    m.start()

    for depth_limit in range(max_limit + 1):
        result = _dls_rec(
            Node(problem.initial_state()), problem, depth_limit, set(), m
        )
        if result is not _CUTOFF and result is not None:
            m.found = True
            m.solution_depth = result.depth
            m.solution_cost  = result.cost
            m.stop(); return result, m

    m.stop(); return None, m


# ══════════════════════════════════════════════════════════════════════════════
# 5. UCS — Uniform-Cost Search  (BFS variant)
# ══════════════════════════════════════════════════════════════════════════════

def ucs(problem: Problem, **_):
    """
    Min-heap ordered by cumulative path cost.
    Optimal for any non-negative step costs.
    Equivalent to BFS when all step costs are equal.

    Complexity — Time: O(b^(1+⌊C*/ε⌋))   Space: O(b^(1+⌊C*/ε⌋))
    """
    m = Metrics(strategy="UCS", problem_name=type(problem).__name__)
    m.start()

    root     = Node(problem.initial_state())
    frontier = [(0.0, root)]        # (cost, node)
    explored = {}                   # state → best cost seen

    while frontier:
        m.max_frontier = max(m.max_frontier, len(frontier))
        cost, node = heapq.heappop(frontier)

        # skip if we already found a cheaper path to this state
        if node.state in explored and explored[node.state] < cost:
            continue
        explored[node.state] = cost
        m.nodes_expanded += 1

        if problem.goal_test(node.state):
            m.found = True
            m.solution_depth = node.depth
            m.solution_cost  = node.cost
            m.stop(); return node, m

        for child in _child_nodes(node, problem, m):
            if child.state not in explored:
                heapq.heappush(frontier, (child.cost, child))

    m.stop(); return None, m


# ══════════════════════════════════════════════════════════════════════════════
# 6. BDS — Bidirectional Search  (BFS variant)
# ══════════════════════════════════════════════════════════════════════════════

def bds(problem: Problem, **_):
    """
    Two simultaneous BFS — forward from initial_state and backward
    from goal_state — stop when frontiers meet.
    Falls back to BFS if problem does not support BDS.

    Complexity — Time: O(b^(d/2))   Space: O(b^(d/2))
    """
    m = Metrics(strategy="BDS", problem_name=type(problem).__name__)
    m.start()

    if not problem.supports_bds():
        # graceful fallback
        m.strategy = "BDS*"
        _, bm = bfs(problem)
        for attr in ("found","nodes_expanded","nodes_generated",
                     "max_frontier","max_depth_seen",
                     "solution_depth","solution_cost"):
            setattr(m, attr, getattr(bm, attr))
        # re-run to get the actual node back
        node, _ = bfs(problem)
        m.stop(); return node, m

    fwd_root = Node(problem.initial_state())
    bwd_root = Node(problem.goal_state())

    fwd_frontier = deque([fwd_root])
    bwd_frontier = deque([bwd_root])
    fwd_visited  = {fwd_root.state: fwd_root}
    bwd_visited  = {bwd_root.state: bwd_root}

    def _step(frontier, visited, other_visited, forward):
        if not frontier:
            return None
        node = frontier.popleft()
        m.nodes_expanded += 1
        actions = (problem.actions(node.state) if forward
                   else problem.reverse_actions(node.state))
        for action in actions:
            s2 = (problem.result(node.state, action) if forward
                  else problem.reverse_result(node.state, action))
            child = Node(s2, node, action,
                         node.cost + problem.step_cost(node.state, action))
            m.nodes_generated += 1
            m.max_depth_seen = max(m.max_depth_seen, child.depth)
            if s2 not in visited:
                visited[s2] = child
                frontier.append(child)
                m.max_frontier = max(m.max_frontier, len(frontier))
            if s2 in other_visited:
                return s2   # meeting point
        return None

    while fwd_frontier or bwd_frontier:
        meet = _step(fwd_frontier, fwd_visited, bwd_visited, True)
        if meet:
            fn = fwd_visited[meet]; bn = bwd_visited[meet]
            m.found = True
            m.solution_depth = fn.depth + bn.depth
            m.solution_cost  = fn.cost  + bn.cost
            m.stop(); return fn, m

        meet = _step(bwd_frontier, bwd_visited, fwd_visited, False)
        if meet:
            fn = fwd_visited[meet]; bn = bwd_visited[meet]
            m.found = True
            m.solution_depth = fn.depth + bn.depth
            m.solution_cost  = fn.cost  + bn.cost
            m.stop(); return fn, m

    m.stop(); return None, m


# ── registry used by main menu ────────────────────────────────────────────────

STRATEGIES = {
    "BFS"  : (bfs,   {}),
    "DFS"  : (dfs,   {}),
    "DLS"  : (dls,   {"limit": 15}),
    "IDDFS": (iddfs, {"max_limit": 50}),
    "UCS"  : (ucs,   {}),
    "BDS"  : (bds,   {}),
}
