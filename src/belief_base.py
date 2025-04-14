from typing import Optional, List

from formula import Implies, Not, And, Formula, Atom


class BeliefBase:
    """Represents the agent's explicit set of beliefs (formulas)."""

    def __init__(self, initial_beliefs: Optional[List[Formula]] = None):
        """
        Initializes the belief base.

        Args:
            initial_beliefs: An optional list of Formula objects to start with.
                             Duplicates will be ignored.
        """
        self.beliefs: List[Formula] = []
        if initial_beliefs:
            for belief in initial_beliefs:
                self.add_belief(belief) # Use add_belief to handle potential duplicates

    def add_belief(self, formula: Formula):
        """
        Adds a formula to the belief base, avoiding duplicates.

        Args:
            formula: The Formula object to add.
        """
        if not isinstance(formula, Formula):
            raise TypeError("Can only add Formula objects to the belief base.")
        if formula not in self.beliefs:
            self.beliefs.append(formula)
            # print(f"DEBUG: Added belief: {formula}") # Optional debug print
        # else:
            # print(f"DEBUG: Belief already present: {formula}") # Optional debug print


    def get_beliefs(self) -> List[Formula]:
        """Returns the list of formulas currently in the belief base."""
        # Return a copy to prevent external modification of the internal list
        return list(self.beliefs)

    def __len__(self) -> int:
        """Returns the number of beliefs in the base."""
        return len(self.beliefs)

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        if not self.beliefs:
            return "BeliefBase{}"
        belief_strs = [str(f) for f in self.beliefs]
        return "BeliefBase{\n  " + ",\n  ".join(belief_strs) + "\n}"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"BeliefBase(initial_beliefs={self.beliefs})"

    def __eq__(self, other):
        """Checks if two belief bases contain the same beliefs (order-independent)."""
        if not isinstance(other, BeliefBase):
            return NotImplemented
        # Use sets for order-independent comparison
        return set(self.beliefs) == set(other.beliefs)

# --- Example Usage ---
if __name__ == "__main__":
    # Make sure formula classes and parser are accessible
    # Example assuming they are in the same file or imported
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    f1 = Implies(p, q)
    f2 = Not(r)
    f3 = And(p, Not(r))

    # Create an empty belief base
    bb1 = BeliefBase()
    print("Empty Belief Base:")
    print(bb1)
    print(f"Length: {len(bb1)}\n")

    # Add beliefs
    bb1.add_belief(f1)
    bb1.add_belief(f2)
    print("After adding f1, f2:")
    print(bb1)
    print(f"Length: {len(bb1)}\n")

    # Add a duplicate
    print("Adding f1 again (should have no effect):")
    bb1.add_belief(f1)
    print(bb1)
    print(f"Length: {len(bb1)}\n")

    # Add another belief
    bb1.add_belief(f3)
    print("After adding f3:")
    print(bb1)
    print(f"Length: {len(bb1)}\n")

    # Create a base with initial beliefs
    bb2 = BeliefBase([Implies(p, q), Not(r), And(p, Not(r))])
    print("Belief Base bb2 created with initial beliefs:")
    print(bb2)

    # Test equality
    print(f"\nbb1 == bb2: {bb1 == bb2}") # Should be True

    bb3 = BeliefBase([Not(r), Implies(p,q)])
    print(f"bb1 == bb3: {bb1 == bb3}") # Should be False (bb1 has f3, bb3 doesn't)
    print(f"bb3 == bb1: {bb3 == bb1}") # Should be False

    # Get beliefs list
    current_beliefs = bb1.get_beliefs()
    print(f"\nRetrieved beliefs from bb1: {current_beliefs}")