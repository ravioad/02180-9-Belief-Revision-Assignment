from typing import Set, FrozenSet, Union, List, Optional, Tuple
from itertools import combinations

from src.logic_utils import Literal, Clause, CNF, to_cnf, cnf_to_string
from src.belief_base import BeliefBase

from src.formula import Atom, Not, Formula, Or
from parser import parse_formula


def get_complement(literal: Literal) -> Literal:
    """Returns the complement of a literal."""
    if isinstance(literal, Not):
        # Complement of ¬p is p
        return literal.operand
    elif isinstance(literal, Atom):
        # Complement of p is ¬p
        return Not(literal)
    else:
        raise TypeError("Input must be a Literal (Atom or Not(Atom))")


def resolve(clause1: Clause, clause2: Clause) -> Set[Clause]:
    """
    Performs the resolution step on two clauses.

    Args:
        clause1: The first clause (a frozenset of Literals).
        clause2: The second clause (a frozenset of Literals).

    Returns:
        A set containing the resolvent clause(s).
        Returns an empty set if no resolution is possible between the two clauses.
        Returns a set containing the empty clause {frozenset()} if a direct
        contradiction (e.g., {p} and {¬p}) is resolved.
    """
    resolvents: Set[Clause] = set()
    resolved_on_literal = False  # Flag to track if any resolution happened

    # Iterate through literals in the first clause
    for lit1 in clause1:
        complement = get_complement(lit1)
        # Check if the complement exists in the second clause
        if complement in clause2:
            resolved_on_literal = True
            # Create the resolvent by combining literals from both clauses,
            # excluding the resolved pair (lit1 and complement).
            combined = (clause1 - {lit1}).union(clause2 - {complement})

            # Factoring: Check for internal contradictions (p and ¬p in the same resolvent)
            has_contradiction = False
            temp_literals = set()
            for lit in combined:
                if get_complement(lit) in combined:
                    has_contradiction = True
                    break  # Tautological resolvent (e.g., p v q v ~p), ignore it
                temp_literals.add(lit)  # Use a temporary set to handle potential internal duplicates cleanly

            if not has_contradiction:
                resolvents.add(frozenset(temp_literals))  # Use temp_literals after check

    # If we resolved p and ~p, the resolvent is the empty set frozenset()
    # This happens if combined is empty after removing lit1 and complement.
    # The above logic handles this: if clause1={lit1} and clause2={complement},
    # combined = {} and frozenset({}) gets added to resolvents.

    return resolvents


# --- Main Resolution Algorithm for Entailment ---

def entails_resolution(belief_base: BeliefBase, query: Formula) -> bool:
    """
    Checks if the belief base entails the query using resolution by refutation.
    KB |= query  <=>  KB ∧ ¬query is unsatisfiable

    Args:
        belief_base: The BeliefBase object containing the KB formulas.
        query: The Formula object representing the query alpha.

    Returns:
        True if KB entails query, False otherwise.
    """
    # print(f"\n--- Checking Entailment: KB |= {query} ---")

    # 1. Negate the query
    negated_query = Not(query)
    # print(f"Negated query: {negated_query}")

    # 2. Combine KB and negated query, convert all to CNF
    clauses: CNF = set()
    all_formulas = belief_base.get_beliefs() + [negated_query]
    # print("Converting formulas to CNF:")
    for f in all_formulas:
        # print(f"  Converting: {f}")
        cnf_f = to_cnf(f)
        # print(f"  Resulting CNF clauses: {cnf_to_string(cnf_f) if cnf_f else '{}'}")
        clauses.update(cnf_f)  # Add all clauses from this formula's CNF

    # print(f"\nInitial combined clauses for resolution: {cnf_to_string(clauses)}")
    if frozenset() in clauses:
        print(
            "Initial clauses contain empty clause (contradiction from start). KB |= query is vacuously true if KB was already contradictory, or ¬query was a tautology.")
        # Technically, if KB is already contradictory, it entails everything.
        # If ¬query is a tautology, KB ∧ ¬query is contradictory.
        # Let's refine: check KB consistency *first*? For now, proceed.
        # If empty clause is immediately present, it means unsatisfiable.
        return True  # KB ^ ~query is unsatisfiable

    # 3. Resolution Loop
    iteration = 0
    while True:
        iteration += 1
        # print(f"\nResolution Iteration {iteration}")
        new_clauses: CNF = set()
        clauses_list = list(clauses)  # Need list for combinations

        # Generate pairs of clauses to resolve
        # Using combinations avoids resolving (A, B) then (B, A) and resolving a clause with itself
        processed_pairs = 0
        for i, j in combinations(range(len(clauses_list)), 2):
            clause1 = clauses_list[i]
            clause2 = clauses_list[j]
            processed_pairs += 1

            resolvents = resolve(clause1, clause2)

            if frozenset() in resolvents:
                # print(f"  Resolved {cnf_to_string({clause1})} and {cnf_to_string({clause2})} -> Empty Clause (⊥)")
                # print("\nEmpty clause derived. KB entails query.")
                return True

            # Add only resolvents that are not already in the main 'clauses' set
            new_clauses.update(resolvents - clauses)
            # Optimization: if resolvents is empty or subset of clauses, 'update' does nothing

        # print(f"  Processed {processed_pairs} pairs in this iteration.")

        if not new_clauses:
            # No new clauses were generated in this iteration
            # print("\nNo new clauses derived. KB does not entail query.")
            return False

        # print(f"  New clauses generated: {cnf_to_string(new_clauses)}")
        # Add the newly derived clauses to the main set for the next iteration
        clauses.update(new_clauses)
        # print(f"  Current clause set size: {len(clauses)}")
        # Optional: print current full set (can be very large)
        # print(f"  Current clauses: {cnf_to_string(clauses)}")

        # Safety break (optional, to prevent infinite loops in case of bugs)
        if iteration > 100:  # Adjust limit as needed
            print("Warning: Resolution exceeded maximum iterations.")
            return False


# --- Example Usage ---
if __name__ == "__main__":
    # Assuming formula classes, parser, BeliefBase, CNF utils defined above

    print("\n--- Resolution Entailment Examples ---")

    # # Example 1: Simple Modus Ponens ( p, p -> q |= q )
    # print("\nExample 1: Modus Ponens")
    # kb1_formulas = [parse_formula("p"), parse_formula("p -> q")]
    # bb1 = BeliefBase(kb1_formulas)
    # q_query = parse_formula("q")
    # result1 = entails_resolution(bb1, q_query)
    # print(f"RESULT: KB |= {q_query}: {result1} (Expected: True)")

    # Example 2: ( p -> q, q -> r |= p -> r )
    # print("\nExample 2: Hypothetical Syllogism")
    # kb2_formulas = [parse_formula("p -> q"), parse_formula("q -> r")]
    # bb2 = BeliefBase(kb2_formulas)
    # pr_query = parse_formula("p -> r")
    # result2 = entails_resolution(bb2, pr_query)
    # print(f"RESULT: KB |= {pr_query}: {result2} (Expected: True)")

    # Example 3: Using the CNF formula from slides (KB |= ¬p ?)
    # KB = (¬r ∨ p ∨ s) ∧ (¬p ∨ r) ∧ (¬s ∨ r) ∧ ¬r
    # print("\nExample 3: Robert lucky/prepared")
    # r = Atom("r")
    # p = Atom("p")
    # s = Atom("s")
    # # Original belief: r ↔ (p ∨ s) AND ¬r
    # # CNF clauses derived before: (¬r ∨ p ∨ s), (¬p ∨ r), (¬s ∨ r), ¬r
    # clause1 = Or(Or(Not(r), p), s)
    # clause2 = Or(Not(p), r)
    # clause3 = Or(Not(s), r)
    # clause4 = Not(r)
    # kb3_formulas = [clause1, clause2, clause3, clause4]
    # bb3 = BeliefBase(kb3_formulas)
    # not_p_query = parse_formula("¬p")  # Query: Robert is not prepared
    # result3 = entails_resolution(bb3, not_p_query)
    # print(f"RESULT: KB |= {not_p_query}: {result3} (Expected: True)")
    #
    # # Example 4: Does KB3 entail 's'? (Should be False)
    # print("\nExample 4: Robert lucky/prepared - False Query")
    # s_query = parse_formula("s")  # Query: Robert is lucky
    # result4 = entails_resolution(bb3, s_query)
    # print(f"RESULT: KB |= {s_query}: {result4} (Expected: False)")

    # Example 5: Contradictory KB ( p, ¬p |= q ) - Anything follows
    print("\nExample 5: Contradictory KB")
    kb5 = BeliefBase([parse_formula("p"), parse_formula("¬p")])
    q_query = parse_formula("q")
    result5 = entails_resolution(kb5, q_query)
    print(f"RESULT: KB |= {q_query}: {result5} (Expected: True)")
