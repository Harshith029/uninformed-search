"""
engine/metrics.py
Collects performance statistics for one search run.
"""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Metrics:
    strategy        : str   = ""
    problem_name    : str   = ""
    nodes_expanded  : int   = 0
    nodes_generated : int   = 0
    max_frontier    : int   = 0
    max_depth_seen  : int   = 0
    solution_depth  : Optional[int]   = None
    solution_cost   : Optional[float] = None
    elapsed_ms      : float = 0.0
    found           : bool  = False
    _t0             : float = field(default=0.0, repr=False)

    def start(self):  self._t0 = time.perf_counter()
    def stop(self):   self.elapsed_ms = (time.perf_counter() - self._t0) * 1000

    def row(self) -> dict:
        return {
            "Strategy"     : self.strategy,
            "Found"        : "✔ Yes" if self.found else "✘ No",
            "Sol. Depth"   : str(self.solution_depth) if self.found else "—",
            "Sol. Cost"    : str(int(self.solution_cost)) if self.found else "—",
            "Expanded"     : str(self.nodes_expanded),
            "Generated"    : str(self.nodes_generated),
            "Max Frontier" : str(self.max_frontier),
            "Max Depth"    : str(self.max_depth_seen),
            "Time (ms)"    : f"{self.elapsed_ms:.3f}",
        }
