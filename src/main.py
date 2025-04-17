from belief_base import BeliefBase
from formula import Atom, Or, Not, Implies
from parser import parse_formula
from resolution import entails_resolution
from belief_revision import contract_partial_meet_priority


def test_resolution():
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

def test_belief_revision_contraction():
    print("\n--- Contraction Examples (with Priority) ---")

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")  # New atom for more complex example

    # Example 1 (Same as before, but check selection)
    # Order: p (priority 0), p->q (priority 1)
    print("\nExample CP1: Contract q from {p, p -> q}")
    f1 = p
    f2 = Implies(p, q)
    bb_c1 = BeliefBase([f1, f2])  # Order matters now for priority
    print(f"Original KB: {bb_c1}")
    contracted_bb_c1 = contract_partial_meet_priority(bb_c1, q)
    print(f"Contracted KB (KB ÷ {q}): {contracted_bb_c1}")
    # Maximal Remainders: {p}, {p->q}
    # Remainder {p}: Excludes {p->q} (priority 1). Max excluded prio = 1.
    # Remainder {p->q}: Excludes {p} (priority 0). Max excluded prio = 0.
    # Selection: We prefer the set that excludes the *lowest* priority item.
    # This means we prefer excluding prio 1 over prio 0. Select {p}.
    # Intersection({p}) = {p}.
    # Expected: BeliefBase({p})
    print(f"Does contracted KB entail {q}? {entails_resolution(contracted_bb_c1, q)} (Expected: False)")
    print(f"Does contracted KB entail {p}? {entails_resolution(contracted_bb_c1, p)} (Expected: True)")


if __name__ == "__main__":
    test_resolution()
    # test_belief_revision_contraction()