from formula import Formula, Not
from belief_base import BeliefBase  # Make sure BeliefBase is imported
from typing import List, Set, Optional
from itertools import combinations

from resolution import entails_resolution


def get_priority(formula: Formula, original_beliefs_list: List[Formula]) -> int:
    """Gets priority based on index (lower index = higher priority). Returns infinity if not found."""
    try:
        return original_beliefs_list.index(formula)
    except ValueError:
        return int('inf')  # Should not happen if formula is from the base


def generate_subsets(elements: List[Formula]):
    """Generates all subsets (including empty) of a list of formulas."""
    n = len(elements)
    for i in range(n + 1):  # Include 0 for empty set
        for combo in combinations(elements, i):
            yield set(combo)


def expand(belief_base: BeliefBase, formula_to_add: Formula) -> BeliefBase:
    """
    Performs Expansion: Adds a formula to the belief base.

    Args:
        belief_base: The initial BeliefBase.
        formula_to_add: The Formula to add.

    Returns:
        A new BeliefBase containing the original beliefs plus the new one.
        (Creates a new object to avoid modifying the original in place).
    """
    print(f"\n--- Expanding KB with {formula_to_add} ---")
    new_beliefs = belief_base.get_beliefs()  # Get a copy
    # Create a new BeliefBase, add_belief handles duplicates
    new_bb = BeliefBase(new_beliefs)
    new_bb.add_belief(formula_to_add)
    print(f"Resulting expanded belief base: {new_bb}")
    return new_bb


def revise(belief_base: BeliefBase, formula_to_revise_with: Formula) -> BeliefBase:
    """
    Performs Revision using the Levi Identity: KB * phi = (KB ÷ ¬phi) + phi.

    Args:
        belief_base: The initial BeliefBase.
        formula_to_revise_with: The Formula (phi) to revise the base with.

    Returns:
        A new BeliefBase representing the revised beliefs.
    """
    print(f"\n--- Revising KB with {formula_to_revise_with} ---")
    phi = formula_to_revise_with
    neg_phi = Not(phi)
    print(f"Using Levi Identity: (KB ÷ {neg_phi}) + {phi}")

    contracted_base = contract_partial_meet_priority(belief_base, neg_phi)

    revised_base = expand(contracted_base, phi)

    print(f"\nFinal Revised Belief Base (KB * {phi}): {revised_base}")
    return revised_base


def contract_partial_meet_priority(belief_base: BeliefBase, formula_to_contract: Formula) -> BeliefBase:
    """
    Performs Partial Meet Contraction based on priority (insertion order).

    Args:
        belief_base: The initial BeliefBase.
        formula_to_contract: The Formula to remove the entailment of.

    Returns:
        A new BeliefBase representing the result of the contraction.
    """
    print(f"\n--- Contracting {formula_to_contract} from KB (with Priority) ---")
    original_beliefs: List[Formula] = belief_base.get_beliefs()  # Keep order!
    phi = formula_to_contract

    # Tautology check (same as before)
    empty_bb = BeliefBase()
    if entails_resolution(empty_bb, phi):
        print(f"Formula {phi} is a tautology. Cannot contract. Returning original KB.")
        return BeliefBase(original_beliefs)

    # 1. Find Remainders (KB ↓ phi) - Maximals that DO NOT entail phi
    # (Finding maximals efficiently is complex, using generate_subsets + filter for simplicity)
    print("Finding potential remainder subsets (that do not entail phi)...")
    potential_remainders: List[Set[Formula]] = []
    for subset_formulas_set in generate_subsets(original_beliefs):
        subset_bb = BeliefBase(list(subset_formulas_set))
        if not entails_resolution(subset_bb, phi):
            potential_remainders.append(subset_formulas_set)
            # print(f"  Potential: {{{', '.join(map(str, subset_formulas_set))}}}") # Very verbose

    print(f"Found {len(potential_remainders)} potential remainders. Filtering for maximality...")
    maximal_remainders: List[Set[Formula]] = []
    potential_remainders.sort(key=len, reverse=True)
    for i, current_subset in enumerate(potential_remainders):
        is_maximal = True
        for maximal_set in maximal_remainders:
            if current_subset.issubset(maximal_set) and current_subset != maximal_set:
                is_maximal = False
                break
        if is_maximal:
            maximal_remainders.append(current_subset)

    print(f"\nFound {len(maximal_remainders)} maximal remainder set(s):")
    # Sort sets before printing for consistent display
    sorted_max_remainders = sorted(maximal_remainders, key=lambda s: tuple(sorted(map(str, s))))
    for rem_set in sorted_max_remainders:
        print(f"  - {{{', '.join(map(str, sorted(list(rem_set), key=str)))}}}")

    if not maximal_remainders:
        # Handle edge case (same as before)
        if entails_resolution(belief_base, phi):
            print("Original KB entailed phi, but no non-entailing subsets found. Returning empty base.")
            return BeliefBase()
        else:
            print("Original KB did not entail phi. Returning original KB (Vacuity).")
            return BeliefBase(original_beliefs)

    # 2. Selection (γ) - Based on Priority (Insertion Order)
    print("\nSelecting best remainders based on priority (earliest added = highest priority):")
    best_remainders: List[Set[Formula]] = []
    # We want to MAXIMIZE the MINIMUM index (priority number) of the excluded formulas
    max_lowest_priority_excluded = -1  # Track the highest index number seen for max excluded priority

    original_belief_set = set(original_beliefs)
    for remainder in maximal_remainders:
        excluded_formulas = original_belief_set - remainder
        if not excluded_formulas:
            # This remainder excludes nothing. Its "max excluded priority index" is effectively infinity (lowest priority).
            current_min_priority_excluded_index = float('inf')
            excluded_str = "None"
        else:
            # Find the highest priority (lowest index) formula excluded by this remainder
            current_min_priority_excluded_index = min(get_priority(f, original_beliefs) for f in excluded_formulas)
            excluded_str = str(current_min_priority_excluded_index)

        print(
            f"  Remainder {{{', '.join(map(str, sorted(list(remainder), key=str)))}}}: Highest priority excluded index = {excluded_str}")
        # We prefer remainders where the highest-priority thing they exclude
        # is actually as low priority (high index) as possible.
        if current_min_priority_excluded_index > max_lowest_priority_excluded:
            # This remainder is better (avoids discarding higher-priority items)
            max_lowest_priority_excluded = current_min_priority_excluded_index
            best_remainders = [remainder]  # Start a new list of best
            print(f"    -> New best found (must discard item with index >= {current_min_priority_excluded_index})")
        elif current_min_priority_excluded_index == max_lowest_priority_excluded:
            # This remainder is equally good as the current best
            best_remainders.append(remainder)
            print(f"    -> Equally good added")

    selected_remainders = best_remainders
    print(f"\nSelected {len(selected_remainders)} best remainder set(s) for intersection:")
    sorted_selected_remainders = sorted(selected_remainders, key=lambda s: tuple(sorted(map(str, s))))
    for rem_set in sorted_selected_remainders:
        print(f"  - {{{', '.join(map(str, sorted(list(rem_set), key=str)))}}}")

    # 3. Intersection
    print("\nCalculating intersection of selected remainders:")
    if not selected_remainders:
        final_beliefs = set()
    else:
        final_beliefs = set(selected_remainders[0])  # Start with a copy
        for i in range(1, len(selected_remainders)):
            final_beliefs.intersection_update(selected_remainders[i])

    print(f"Resulting contracted belief set: {{{', '.join(map(str, sorted(list(final_beliefs), key=str)))}}}")

    contracted_bb = BeliefBase(list(final_beliefs))
    return contracted_bb
