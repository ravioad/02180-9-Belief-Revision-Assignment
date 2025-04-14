from src.old.belief_base import BeliefBase
from src.old.resolution import entails

if __name__ == "__main__":
    bb = BeliefBase()

    bb.add_formula([['¬r', 'p', 's']])  # (¬r ∨ p ∨ s)
    bb.add_formula([['¬p', 'r']])  # (¬p ∨ r)
    bb.add_formula([['¬s', 'r']])  # (¬s ∨ r)
    bb.add_formula([['¬r']])  # (¬r)

    bb.show()
    print("All clauses:", bb.get_all_clauses())

    # Query
    query = 't'

    # # Belief base with unrelated formulas
    # bb.add_formula([['p', 'q', 's']])       # (p ∨ q)
    # bb.add_formula([['¬r', 's']])      # (¬r ∨ s)
    # bb.add_formula([['¬q', 'r']])      # (¬q ∨ r)
    #
    # bb.show()
    # print("All clauses:", bb.get_all_clauses())
    #
    # # Query
    # query = 't'  # Not related to anything in the base

    # Check entailment
    result = entails(bb.get_all_clauses(), query)
    print("Does belief base entail", query, "?", result)
