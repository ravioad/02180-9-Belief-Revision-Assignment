class BeliefBase:
    def __init__(self):
        self.base = []  # List of CNF formulas (each is a list of clauses)

    def add_formula(self, cnf_formula):
        """Add a CNF formula to the belief base."""
        self.base.append(cnf_formula)

    def remove_formula(self, cnf_formula):
        """Remove a CNF formula from the belief base."""
        if cnf_formula in self.base:
            self.base.remove(cnf_formula)

    def show(self):
        """Print the current belief base."""
        for i, formula in enumerate(self.base):
            print(f"Formula {i + 1}: {formula}")

    def get_all_clauses(self):
        """Flatten all formulas in the belief base into one list of clauses."""
        all_clauses = []
        for formula in self.base:
            all_clauses.extend(formula)
        return all_clauses