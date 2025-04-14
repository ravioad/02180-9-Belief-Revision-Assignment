from belief_base import BeliefBase
from formula import Atom, Or, Not
from parser import parse_formula
from resolution import entails_resolution

if __name__ == "__main__":
    # Example 3: Using the CNF formula from slides (KB |= ¬p ?)
    # KB = (¬r ∨ p ∨ s) ∧ (¬p ∨ r) ∧ (¬s ∨ r) ∧ ¬r
    print("\nExample 3: Robert lucky/prepared")
    r = Atom("r")
    p = Atom("p")
    s = Atom("s")
    # Original belief: r ↔ (p ∨ s) AND ¬r
    # CNF clauses derived before: (¬r ∨ p ∨ s), (¬p ∨ r), (¬s ∨ r), ¬r
    clause1 = Or(Or(Not(r), p), s)
    clause2 = Or(Not(p), r)
    clause3 = Or(Not(s), r)
    clause4 = Not(r)
    kb3_formulas = [clause1, clause2, clause3, clause4]
    bb3 = BeliefBase(kb3_formulas)
    not_p_query = parse_formula("¬p")  # Query: Robert is not prepared
    result3 = entails_resolution(bb3, not_p_query)
    print(f"RESULT: KB |= {not_p_query}: {result3} (Expected: True)")

    # Example 4: Does KB3 entail 's'? (Should be False)
    print("\nExample 4: Robert lucky/prepared - False Query")
    s_query = parse_formula("s")  # Query: Robert is lucky
    result4 = entails_resolution(bb3, s_query)
    print(f"RESULT: KB |= {s_query}: {result4} (Expected: False)")
