from itertools import combinations
from typing import Set

from belief_base import BeliefBase
from formula import Atom, Not, Formula
from logic_utils import Literal, Clause, CNF, to_cnf


def get_complement(literal: Literal) -> Literal:
    if isinstance(literal, Not):
        # Complement of ¬p is p
        return literal.operand
    elif isinstance(literal, Atom):
        # Complement of p is ¬p
        return Not(literal)
    else:
        raise TypeError("Input must be a Literal (Atom or Not(Atom))")


def resolve(clause1: Clause, clause2: Clause) -> Set[Clause]:
    resolvents: Set[Clause] = set()

    # Iterate through literals in the first clause
    for lit1 in clause1:
        complement = get_complement(lit1)
        # Check if the complement exists in the second clause
        if complement in clause2:
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

    return resolvents


def entails_resolution(belief_base: BeliefBase, query: Formula) -> bool:
    # 1. Negate the query
    negated_query = Not(query)

    # 2. Combine KB and negated query, convert all to CNF
    clauses: CNF = set()
    all_formulas = belief_base.get_beliefs() + [negated_query]

    for f in all_formulas:
        cnf_f = to_cnf(f)
        clauses.update(cnf_f)  # Add all clauses from this formula's CNF

    if frozenset() in clauses:
        print(
            "Initial clauses contain empty clause (contradiction from start). KB |= query is vacuously true if KB was already contradictory, or ¬query was a tautology.")
        return True  # KB ^ ~query is unsatisfiable

    # 3. Resolution Loop
    iteration = 0
    while True:
        iteration += 1
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
                # print("\nEmpty clause derived. KB entails query.")
                return True

            # Add only resolvents that are not already in the main 'clauses' set
            new_clauses.update(resolvents - clauses)

        if not new_clauses:
            # print("\nNo new clauses derived. KB does not entail query.")
            return False

        # Add the newly derived clauses to the main set for the next iteration
        clauses.update(new_clauses)

        # Safety break (to prevent infinite loops in case of bugs)
        if iteration > 100:
            print("Warning: Resolution exceeded maximum iterations.")
            return False
