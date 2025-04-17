from belief_base import BeliefBase
from formula import Atom, Or, Not, Implies, Iff
from parser import parse_formula
from resolution import entails_resolution
from belief_revision import contract_partial_meet_priority, revise


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


def more_test_cases_belief_revision():
    print("\n--- More Contraction Examples (with Priority) ---")

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    s = Atom("s")
    #
    # # Example CP4: Priority Tie-breaking needed?
    # # KB = {p, q, p -> r, q -> r}, Contract r
    # # Order: p (0), q (1), p->r (2), q->r (3)
    # print("\nExample CP4: Tie-breaking?")
    # f_p_imp_r = Implies(p, r)
    # f_q_imp_r = Implies(q, r)
    # # Original beliefs list determines priority
    # bb_c4_beliefs = [p, q, f_p_imp_r, f_q_imp_r]
    # bb_c4 = BeliefBase(bb_c4_beliefs)
    # print(f"Original KB: {bb_c4}")
    # contracted_bb_c4 = contract_partial_meet_priority(bb_c4, r)
    # print(f"Contracted KB (KB ÷ {r}): {contracted_bb_c4}")
    # # Expected: BeliefBase({p, q}) - based on trace in previous thought
    # print(f"Does contracted KB entail {r}? {entails_resolution(contracted_bb_c4, r)} (Expected: False)")
    # print(f"Does contracted KB entail {p}? {entails_resolution(contracted_bb_c4, p)} (Expected: True)")
    # print(f"Does contracted KB entail {q}? {entails_resolution(contracted_bb_c4, q)} (Expected: True)")

    # # Example CP5: Different Priority Order for CP4
    # # KB = {p -> r, q -> r, p, q}, Contract r
    # # Order: p->r (0), q->r (1), p (2), q (3)
    # print("\nExample CP5: Different priority order")
    # # Original beliefs list determines priority
    # bb_c5_beliefs = [f_p_imp_r, f_q_imp_r, p, q]
    # bb_c5 = BeliefBase(bb_c5_beliefs)
    # print(f"Original KB: {bb_c5}")
    # contracted_bb_c5 = contract_partial_meet_priority(bb_c5, r)
    # print(f"Contracted KB (KB ÷ {r}): {contracted_bb_c5}")
    # # Expected: BeliefBase({p -> r, q -> r}) - based on trace in previous thought
    # print(f"Does contracted KB entail {r}? {entails_resolution(contracted_bb_c5, r)} (Expected: False)")
    # # Check if implications are still there
    # print(f"Does contracted KB entail {f_p_imp_r}? {entails_resolution(contracted_bb_c5, f_p_imp_r)} (Expected: True)")
    # print(f"Does contracted KB entail {f_q_imp_r}? {entails_resolution(contracted_bb_c5, f_q_imp_r)} (Expected: True)")
    # Example CP6: Intersection resulting in only tautologies (empty base)
    # KB = {p -> q, q -> p}, Contract q (or p)
    # Order: p->q (0), q->p (1)

    # print("\nExample CP6: Intersection leads to empty base?")
    # f_p_imp_q = Implies(p, q)
    # f_q_imp_p = Implies(q, p)
    # bb_c6_beliefs = [f_p_imp_q, f_q_imp_p]
    # bb_c6 = BeliefBase(bb_c6_beliefs)
    # print(f"Original KB: {bb_c6}")
    # # Does KB entail q? No. p=0, q=0 makes KB true but q false.
    # # Does KB entail p? No. p=0, q=0 makes KB true but p false.
    # # Let's contract something entailed, e.g. p <-> q
    # f_p_iff_q = Iff(p, q)
    # # Does KB entail p<->q? Yes. ((~p V q) & (~q V p)) & ~(p<->q)
    # # => ((~p V q) & (~q V p)) & ~((~p V q) & (~q V p)) => False. Entailed.
    # contracted_bb_c6 = contract_partial_meet_priority(bb_c6, f_p_iff_q)
    # print(f"Contracted KB (KB ÷ {f_p_iff_q}): {contracted_bb_c6}")
    # # Subsets: {}, {p->q}, {q->p}, {p->q, q->p}
    # # Entail p<->q?
    # # {}? No.
    # # {p->q}? No. (p=0, q=1 makes p->q T, p<->q F)
    # # {q->p}? No. (p=1, q=0 makes q->p T, p<->q F)
    # # {p->q, q->p}? Yes.
    # # Potential remainders: {}, {p->q}, {q->p}
    # # Maximal remainders: {p->q}, {q->p}
    # # Priority selection:
    # # Remainder {p->q}: Excludes {q->p (prio 1)}. Min excluded = 1.
    # # Remainder {q->p}: Excludes {p->q (prio 0)}. Min excluded = 0.
    # # Max of mins = 1. Select {p->q}.
    # # Intersection: {p->q}.
    # # Expected: BeliefBase({p -> q})
    # print(f"Does contracted KB entail {f_p_iff_q}? {entails_resolution(contracted_bb_c6, f_p_iff_q)} (Expected: False)")
    # print(f"Does contracted KB entail {f_p_imp_q}? {entails_resolution(contracted_bb_c6, f_p_imp_q)} (Expected: True)")

    # Example CP7: More complex case
    # KB = {p, p -> q, q -> r, s}, Contract r
    # Order: p(0), p->q(1), q->r(2), s(3)
    print("\nExample CP7: More complex chain")
    f_p_imp_q = Implies(p, q)
    f_q_imp_r = Implies(q, r)
    bb_c7_beliefs = [p, f_p_imp_q, f_q_imp_r, s]
    bb_c7 = BeliefBase(bb_c7_beliefs)
    print(f"Original KB: {bb_c7}")
    # Does KB entail r? Yes. (p, p->q => q; q, q->r => r)
    contracted_bb_c7 = contract_partial_meet_priority(bb_c7, r)
    print(f"Contracted KB (KB ÷ {r}): {contracted_bb_c7}")
    # To not entail r, we must break the chain p -> q -> r.
    # We need to remove p, OR p->q, OR q->r.
    # Maximal subsets not entailing r:
    # {p, p->q, s} (removed q->r)
    # {p, q->r, s} (removed p->q)
    # {p->q, q->r, s} (removed p)
    # Priority Selection:
    # Remainder {p(0), p->q(1), s(3)}: Excludes {q->r(2)}. Min excluded = 2.
    # Remainder {p(0), q->r(2), s(3)}: Excludes {p->q(1)}. Min excluded = 1.
    # Remainder {p->q(1), q->r(2), s(3)}: Excludes {p(0)}. Min excluded = 0.
    # Max of mins = 2. Select {p, p->q, s}.
    # Intersection: {p, p->q, s}.
    # Expected: BeliefBase({p, p -> q, s})
    print(f"Does contracted KB entail {r}? {entails_resolution(contracted_bb_c7, r)} (Expected: False)")
    print(f"Does contracted KB entail {s}? {entails_resolution(contracted_bb_c7, s)} (Expected: True)")
    print(f"Does contracted KB entail {q}? {entails_resolution(contracted_bb_c7, q)} (Expected: True)")


def test_belief_base_revision():
    print("\n--- Revision Examples ---")

    p = Atom("p")
    q = Atom("q")
    not_p = Not(p)
    not_q = Not(q)
    p_implies_q = Implies(p, q)

    # Example R1: Revise {p, p -> q} with ¬q
    # Expected: Should contract ¬(¬q) i.e. q, then expand with ¬q.
    #           Contraction of q from {p, p->q} resulted in {p}.
    #           Expansion of {p} with ¬q results in {p, ¬q}.
    # print("\nExample R1: Revise {p, p -> q} with ¬q")
    # bb_r1 = BeliefBase([p, p_implies_q])
    # print(f"Original KB: {bb_r1}")
    # revised_bb_r1 = revise(bb_r1, not_q)
    # print(f"RESULT: {revised_bb_r1}")
    # # Verify expected results
    # expected_bb_r1 = BeliefBase([p, not_q])
    # print(f"Matches expected {{p, ¬q}}? {revised_bb_r1 == expected_bb_r1}")
    # print(f"Does revised KB entail {not_q}? {entails_resolution(revised_bb_r1, not_q)} (Expected: True)")
    # print(
    #     f"Does revised KB entail {p_implies_q}? {entails_resolution(revised_bb_r1, p_implies_q)} (Expected: False)")  # Should have been removed
    # print(f"Does revised KB entail {p}? {entails_resolution(revised_bb_r1, p)} (Expected: True)")  # Should remain

    # Example R2: Revise {p} with q (Simple expansion as ¬q is not in KB)
    # Expected: Should contract ¬q. {p} doesn't entail ¬q. Vacuity applies.
    #           Contraction({p}, ¬q) returns {p}.
    #           Expansion({p}, q) returns {p, q}.

    # print("\nExample R2: Revise {p} with q")
    # bb_r2 = BeliefBase([p])
    # print(f"Original KB: {bb_r2}")
    # revised_bb_r2 = revise(bb_r2, q)
    # print(f"RESULT: {revised_bb_r2}")
    # # Verify expected results
    # expected_bb_r2 = BeliefBase([p, q])
    # print(f"Matches expected {{p, q}}? {revised_bb_r2 == expected_bb_r2}")

    # Example R3: Revise {p, ¬p} with q (Contradictory base)
    # Expected: Behaviour with contradictory bases can be tricky for contraction.
    #           Let's trace: Contract ¬q from {p, ¬p}.
    #           Any subset of {p, ¬p} is contradictory and entails ¬q.
    #           contract_partial_meet_priority should return BeliefBase().
    #           Expand({}, q) returns {q}.
    # print("\nExample R3: Revise {p, ¬p} with q")
    # bb_r3 = BeliefBase([p, not_p])
    # print(f"Original KB: {bb_r3}")
    # revised_bb_r3 = revise(bb_r3, q)
    # print(f"RESULT: {revised_bb_r3}")
    # # Verify expected results
    # expected_bb_r3 = BeliefBase([q])
    # print(f"Matches expected {{q}}? {revised_bb_r3 == expected_bb_r3}")

    # Example R4: Revise {q} with p -> q (Tautology check in revise?)
    # Let's revise with something entailed but not a tautology.
    # Revise {p, p -> q} with q
    # Expected: Contract ¬q from {p, p->q}. Result {p}.
    #           Expand {p} with q. Result {p, q}.
    print("\nExample R4: Revise {p, p -> q} with q")
    bb_r4 = BeliefBase([p, p_implies_q])
    print(f"Original KB: {bb_r4}")
    revised_bb_r4 = revise(bb_r4, q)
    print(f"RESULT: {revised_bb_r4}")
    expected_bb_r4 = BeliefBase([p, q])
    print(f"Matches expected {{p, q}}? {revised_bb_r4 == expected_bb_r4}")
if __name__ == "__main__":
    # test_resolution()
    # test_belief_revision_contraction()
    # more_test_cases_belief_revision()
    test_belief_base_revision()
