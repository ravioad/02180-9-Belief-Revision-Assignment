from typing import Optional, List

from src.formula import Formula


class BeliefBase:

    def __init__(self, initial_beliefs: Optional[List[Formula]] = None):
        self.beliefs: List[Formula] = []
        if initial_beliefs:
            for belief in initial_beliefs:
                self.add_belief(belief)

    def add_belief(self, formula: Formula):
        if not isinstance(formula, Formula):
            raise TypeError("Can only add Formula objects to the belief base.")
        if formula not in self.beliefs:
            self.beliefs.append(formula)

    def get_beliefs(self) -> List[Formula]:
        return list(self.beliefs)

    def __len__(self) -> int:
        return len(self.beliefs)

    def __str__(self) -> str:
        if not self.beliefs:
            return "BeliefBase{}"
        belief_strs = [str(f) for f in self.beliefs]
        return "BeliefBase{\n  " + ",\n  ".join(belief_strs) + "\n}"

    def __repr__(self) -> str:
        return f"BeliefBase(initial_beliefs={self.beliefs})"

    def __eq__(self, other):
        if not isinstance(other, BeliefBase):
            return NotImplemented
        return set(self.beliefs) == set(other.beliefs)
