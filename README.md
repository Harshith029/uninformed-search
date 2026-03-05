# Uninformed Search Strategies — Terminal Implementation

Artificial Intelligence course demonstration. - Individual Assignment
BFS, DFS, and their variants applied to four classical AI search problems.

---

## Members

| Name | Roll Number |
|---|---|
| Pali Krishna Harshith | SE24UCSE001 |

---

## Concept

### Uninformed (Blind) Search

Uninformed search strategies operate without any domain-specific knowledge beyond the problem definition. They cannot estimate how far they are from the goal — they explore the state space by systematically generating children, checking goal conditions, and managing frontiers.

```
BFS Family (breadth-based)          DFS Family (depth-based)
──────────────────────────          ────────────────────────────────
BFS   Breadth-First Search          DFS   Depth-First Search
UCS   Uniform-Cost Search           DLS   Depth-Limited Search
BDS   Bidirectional Search          IDDFS Iterative Deepening DFS
```

---

## Strategies

### 1. BFS — Breadth-First Search

FIFO queue. Explores all nodes at depth d before any at d+1.
Guarantees the **shortest path** (fewest steps) for unit-cost problems.

| Property | Value |
|---|---|
| Complete | Yes |
| Optimal | Yes (unit costs) |
| Time | O(b^d) |
| Space | O(b^d) — keeps all nodes in memory |

### 2. DFS — Depth-First Search

LIFO stack. Explores as deep as possible before backtracking.
Memory-efficient; may find a non-optimal (longer) solution.

| Property | Value |
|---|---|
| Complete | Yes (finite, acyclic graphs) |
| Optimal | No |
| Time | O(b^m) |
| Space | O(b·m) — only current path stored |

### 3. DLS — Depth-Limited Search *(DFS variant)*

DFS with a hard depth cutoff L. Prevents infinite loops in cyclic state spaces.

| Property | Value |
|---|---|
| Complete | Only if solution depth ≤ L |
| Optimal | No |
| Time | O(b^L) |
| Space | O(b·L) |

### 4. IDDFS — Iterative Deepening DFS *(DFS variant)*

Runs DLS at increasing limits (0, 1, 2, …). The best of both worlds — BFS optimality with DFS memory footprint.

| Property | Value |
|---|---|
| Complete | Yes |
| Optimal | Yes (unit costs) |
| Time | O(b^d) — repeated shallow work is asymptotically negligible |
| Space | O(b·d) |

### 5. UCS — Uniform-Cost Search *(BFS variant)*

Min-heap ordered by cumulative path cost. Optimal for any non-negative step costs. Identical to BFS when all step costs equal 1.

| Property | Value |
|---|---|
| Complete | Yes (non-negative costs) |
| Optimal | Yes |
| Time | O(b^(1+⌊C*/ε⌋)) |
| Space | O(b^(1+⌊C*/ε⌋)) |

### 6. BDS — Bidirectional Search *(BFS variant)*

Two simultaneous BFS — forward from `initial_state` and backward from `goal_state` — halting when frontiers meet. Dramatically reduces search effort.

| Property | Value |
|---|---|
| Complete | Yes |
| Optimal | Yes (unit costs) |
| Time | O(b^(d/2)) |
| Space | O(b^(d/2)) |
| Requires | Concrete goal state + reverse operators |

---

## Architecture

```
+------------------------------------------------------------------+
|                    SEARCH ENGINE                                 |
|                                                                  |
|  Problem (abstract base)                                         |
|    initial_state()   goal_test(s)                                |
|    actions(s)        result(s,a)    step_cost(s,a)               |
|    goal_state()      reverse_actions(s)   reverse_result(s,a)   |
|        │                                                         |
|        ▼                                                         |
|  Node                                                            |
|    state · parent · action · depth · cost                        |
|    path_states()    path_actions()                               |
|        │                                                         |
|        ▼                                                         |
|  Strategy                                                        |
|    BFS   → deque (FIFO)           optimal, high memory           |
|    DFS   → list  (LIFO stack)     low memory, not optimal        |
|    DLS   → recursive DFS + limit  avoids cyclic loops            |
|    IDDFS → DLS with rising limit  optimal + low memory           |
|    UCS   → heapq (min cost)       optimal for any step cost      |
|    BDS   → two deques fwd+bwd     halves effective depth         |
|        │                                                         |
|        ▼                                                         |
|  Metrics                                                         |
|    nodes_expanded · nodes_generated · max_frontier               |
|    solution_depth · solution_cost   · elapsed_ms                 |
+------------------------------------------------------------------+
```

---

## Project Structure

```
uninformed-search/
│
├── main.py                   Entry point — menus, runners, solution display
│
├── engine/
│   ├── node.py               Search node: state, parent, action, depth, cost
│   ├── problem.py            Abstract Problem base class
│   ├── metrics.py            Performance data (expansions, time, depth, cost)
│   └── strategies.py         All 6 strategies (BFS/DFS/DLS/IDDFS/UCS/BDS)
│
├── problems/
│   ├── water_jug.py          Milk & Water Jug (3 variants + custom)
│   ├── missionaries.py       Missionaries & Cannibals
│   ├── eight_queens.py       Eight Queens (N=8, column-by-column)
│   └── tic_tac_toe.py        Tic-Tac-Toe (X wins from empty board)
│
└── compare/
    └── table.py              Comparison table + 6-metric analysis
```

---

## Problems

### 1. Milk & Water Jug Problem

Two jugs with no measuring marks. Goal: measure exactly GOAL litres using fill, empty, and pour operations.

**State**: `(a, b)` — current fill levels
**Actions**: fill_a, fill_b, empty_a, empty_b, pour_a→b, pour_b→a
**Goal**: GOAL ∈ state
**BDS**: Supported

| Variant | Jug A | Jug B | Goal |
|---|---|---|---|
| Classic | 4L | 3L | 2L |
| Medium | 5L | 3L | 4L |
| Hard | 8L | 5L | 6L |
| Custom | any | any | any |

### 2. Missionaries and Cannibals

3 missionaries + 3 cannibals must cross a river. Boat holds 1–2 people. Cannibals must never outnumber missionaries on either bank.

**State**: `(m_left, c_left, boat_side)`
**Actions**: move 1M, 1C, 1M+1C, 2M, or 2C
**Goal**: `(0, 0, 'R')`
**BDS**: Supported

Optimal solution: 11 moves.

### 3. Eight Queens

Place 8 queens on an 8×8 chessboard so no two attack each other.

**State**: tuple of length 0–8, `state[col] = row`
**Actions**: valid row placements for the next column (column conflicts prevented by construction)
**Goal**: all 8 queens placed with no conflicts
**BDS**: Not applicable (no meaningful reverse for partial placements)

One solution: A1, B5, C8, D6, E3, F7, G2, H4

### 4. Tic-Tac-Toe

Search for a winning move sequence for X from an empty board.

**State**: 9-tuple of `' '`, `'X'`, `'O'`
**Actions**: index of empty cell (0–8)
**Goal**: X has three in a row
**BDS**: Not practical (too many possible goal boards)

BFS finds the minimum-depth (5-move) X win. DFS finds any win in just 8 expansions.

---

## Performance Results

### Water Jug (Classic: 4L + 3L → 2L)

| Strategy | Found | Depth | Expanded | Time (ms) |
|---|---|---|---|---|
| BFS | ✔ | 4 | 8 | ~0.07 |
| DFS | ✔ | 6 | 7 | ~0.03 |
| DLS | ✔ | 6 | 6 | ~0.02 |
| IDDFS | ✔ | 4 | 25 | ~0.07 |
| UCS | ✔ | 4 | 11 | ~0.04 |
| **BDS** | **✔** | **2** | **2** | **~0.01** |

### Missionaries & Cannibals

| Strategy | Found | Depth | Expanded | Time (ms) |
|---|---|---|---|---|
| BFS | ✔ | 11 | 13 | ~0.2 |
| DFS | ✔ | 11 | 14 | ~0.2 |
| DLS | ✔ | 11 | 12 | ~0.2 |
| IDDFS | ✔ | 11 | 136 | ~1.0 |
| UCS | ✔ | 11 | 25 | ~0.3 |
| BDS | ✔ | 11 | 15 | ~0.2 |

### Eight Queens

| Strategy | Found | Depth | Expanded | Note |
|---|---|---|---|---|
| BFS | ✔ | 8 | 1665 | Explores all shallow partial placements |
| **DFS** | **✔** | **8** | **114** | **Best for this problem** |
| DLS(L=8) | ✔ | 8 | 113 | Same as DFS at correct limit |
| IDDFS | ✔ | 8 | 3656 | Re-expands shallow levels repeatedly |
| UCS | ✔ | 8 | 1966 | Like BFS (unit costs) |

### Tic-Tac-Toe

| Strategy | Found | Depth | Expanded |
|---|---|---|---|
| **BFS** | **✔** | **5** | **341** | **Shortest winning sequence** |
| **DFS** | **✔** | **7** | **8** | **Fastest by expansions** |
| DLS(L=9) | ✔ | 7 | 7 | Slightly fewer than DFS |
| IDDFS | ✔ | 5 | 691 | Optimal depth, high expansion count |
| UCS | ✔ | 5 | 3615 | Very slow — large equal-cost frontier |

---

## Key Observations

**BFS** is always optimal (shortest path) but memory-hungry. It struggles with Eight Queens where the branching factor is large.

**DFS** uses minimal memory and is extremely fast on problems like Eight Queens and Tic-Tac-Toe where any solution is acceptable. But it may find a much longer path than necessary.

**DLS** matches DFS when the limit is set correctly. Setting the limit too low gives no solution; too high wastes time.

**IDDFS** is the recommended general-purpose uninformed strategy — it matches BFS for solution quality and DFS for memory. The repeated re-expansion cost is mathematically small (adds only a factor of b/(b-1)).

**UCS** is identical to BFS on unit-cost problems (all four here). Its advantage becomes visible when step costs vary.

**BDS** dominates all others when supported — only 2 node expansions on the Water Jug problem by meeting in the middle. It requires a concrete, reachable goal state and reverse operators.

---

## Setup

No external libraries required. Pure Python standard library.

```bash
python main.py
```

### Step 1 — Clone the repository

```bash
git clone https://github.com/Harshith029/uninformed-search.git
cd uninformed-search
```

### Step 2 — Run

```bash
python main.py
```

```
MAIN MENU
  [1]  Milk & Water Jug Problem      — 3 variants + custom
  [2]  Missionaries & Cannibals      — classic river crossing
  [3]  Eight Queens                  — N=8 chessboard
  [4]  Tic-Tac-Toe                   — X wins from empty board
  [5]  Compare All Problems          — all strategies × all problems
  [6]  Strategy Reference Guide      — theory & complexity
  [Q]  Quit
```

After selecting a problem, all six strategies run automatically. A formatted comparison table is printed with 6 performance metrics, followed by an analysis naming the winner in each category. You can then select any strategy to view its full step-by-step solution path.

---

## References

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach*, 4th Ed. Chapter 3: Solving Problems by Searching.
- Korf, R. E. (1985). Depth-first iterative-deepening: An optimal admissible tree search. *Artificial Intelligence*, 27(1), 97–109.
- Pohl, I. (1971). Bi-directional search. *Machine Intelligence*, 6, 127–140.
