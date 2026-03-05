"""
engine/problem.py
Abstract base class every search problem must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, List


class Problem(ABC):

    @abstractmethod
    def initial_state(self) -> Any: ...

    @abstractmethod
    def goal_test(self, state: Any) -> bool: ...

    @abstractmethod
    def actions(self, state: Any) -> List[Any]: ...

    @abstractmethod
    def result(self, state: Any, action: Any) -> Any: ...

    def step_cost(self, state: Any, action: Any) -> float:
        return 1.0

    def action_label(self, action: Any) -> str:
        return str(action)

    # Optional BDS support — problems that can define a concrete goal state
    # and reverse operators should implement these.
    def goal_state(self):
        raise NotImplementedError

    def reverse_actions(self, state):
        raise NotImplementedError

    def reverse_result(self, state, action):
        raise NotImplementedError

    def supports_bds(self) -> bool:
        try:
            self.goal_state()
            return True
        except NotImplementedError:
            return False
