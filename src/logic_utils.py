from formula import Formula, Atom, Not, And, Or, Implies, Iff  # Ensure these are imported
from parser import parse_formula
from typing import Set, FrozenSet, Union, List, Optional, Tuple

# Define a type alias for literals for clarity
Literal = Union[Atom, Not]
# Define a type alias for clauses (set of literals)
Clause = FrozenSet[Literal]
# Define a type alias for CNF (set of clauses)
CNF = Set[Clause]



def is_literal(formula: Formula) -> bool:
    """Checks if a formula is a literal (Atom or Not(Atom))."""
    return isinstance(formula, Atom) or (isinstance(formula, Not) and isinstance(formula.operand, Atom))


def formula_to_literal(formula: Formula) -> Optional[Literal]:
    """Converts a formula to a literal if possible, else None."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not) and isinstance(formula.operand, Atom):
        return formula
    return None


def _eliminate_implications(formula: Formula) -> Formula:
    """Step 1: Eliminate ↔ and →."""
    if is_literal(formula):
        return formula
    if isinstance(formula, Not):
        return Not(_eliminate_implications(formula.operand))
    if isinstance(formula, And):
        return And(_eliminate_implications(formula.left),
                   _eliminate_implications(formula.right))
    if isinstance(formula, Or):
        return Or(_eliminate_implications(formula.left),
                  _eliminate_implications(formula.right))
    if isinstance(formula, Implies):
        # Replace a → b with ¬a ∨ b
        return Or(Not(_eliminate_implications(formula.left)),
                  _eliminate_implications(formula.right))
    if isinstance(formula, Iff):
        # Replace a ↔ b with (a → b) ∧ (b → a)
        # Then eliminate the inner implications immediately
        left_implies_right = Or(Not(_eliminate_implications(formula.left)),
                                _eliminate_implications(formula.right))
        right_implies_left = Or(Not(_eliminate_implications(formula.right)),
                                _eliminate_implications(formula.left))
        return And(left_implies_right, right_implies_left)
    raise TypeError(f"Unsupported formula type during implication elimination: {type(formula)}")


def _move_negation_inwards(formula: Formula) -> Formula:
    """Step 2: Move ¬ inwards using De Morgan's laws and double negation."""
    if is_literal(formula):
        return formula
    if isinstance(formula, And):
        return And(_move_negation_inwards(formula.left),
                   _move_negation_inwards(formula.right))
    if isinstance(formula, Or):
        return Or(_move_negation_inwards(formula.left),
                  _move_negation_inwards(formula.right))
    if isinstance(formula, Not):
        operand = formula.operand
        if isinstance(operand, Not):
            # ¬(¬a) becomes a
            return _move_negation_inwards(operand.operand)
        if isinstance(operand, And):
            # ¬(a ∧ b) becomes ¬a ∨ ¬b
            return Or(_move_negation_inwards(Not(operand.left)),
                      _move_negation_inwards(Not(operand.right)))
        if isinstance(operand, Or):
            # ¬(a ∨ b) becomes ¬a ∧ ¬b
            return And(_move_negation_inwards(Not(operand.left)),
                       _move_negation_inwards(Not(operand.right)))
        # If operand is an Atom, it's already a literal (handled at start)
        # If operand was Implies/Iff, they should have been eliminated earlier
        raise TypeError(f"Unexpected operand type for Not during NNF conversion: {type(operand)}")

    # Should not reach here if implications were eliminated
    raise TypeError(f"Unexpected formula type during NNF conversion: {type(formula)}")


def _distribute_or_over_and(formula: Formula) -> Formula:
    """Step 3: Distribute ∨ over ∧."""
    if is_literal(formula):
        return formula
    if isinstance(formula, Not):  # Should only be Not(Atom) at this stage
        return formula
    if isinstance(formula, And):
        # Recursively distribute in children
        return And(_distribute_or_over_and(formula.left),
                   _distribute_or_over_and(formula.right))
    if isinstance(formula, Or):
        left = _distribute_or_over_and(formula.left)
        right = _distribute_or_over_and(formula.right)

        # Apply distribution law: a ∨ (b ∧ c) ≡ (a ∨ b) ∧ (a ∨ c)
        if isinstance(right, And):
            # left ∨ (right.left ∧ right.right)
            new_left = _distribute_or_over_and(Or(left, right.left))
            new_right = _distribute_or_over_and(Or(left, right.right))
            return And(new_left, new_right)
        if isinstance(left, And):
            # (left.left ∧ left.right) ∨ right
            new_left = _distribute_or_over_and(Or(left.left, right))
            new_right = _distribute_or_over_and(Or(left.right, right))
            return And(new_left, new_right)
        # If neither child is And, just return the Or (potentially simplified)
        return Or(left, right)  # Already distributed

    raise TypeError(f"Unexpected formula type during distribution: {type(formula)}")


def _collect_clauses(formula: Formula) -> CNF:
    """Helper to collect clauses from a formula already in CNF structure."""
    if isinstance(formula, And):
        # Combine clauses from both sides
        return _collect_clauses(formula.left).union(_collect_clauses(formula.right))
    elif isinstance(formula, Or):
        # Literals within an Or form a single clause
        literals: Set[Literal] = set()
        queue = [formula]
        while queue:
            f = queue.pop(0)
            if isinstance(f, Or):
                queue.append(f.left)
                queue.append(f.right)
            elif is_literal(f):
                literal = formula_to_literal(f)
                if literal:  # Should always be true if is_literal is true
                    # Check for tautology within clause: p ∨ ¬p
                    neg_literal = Not(literal.operand) if isinstance(literal, Not) else Not(literal)
                    if neg_literal in literals:
                        return set()  # Clause is tautological (p V ~p), effectively True, ignore it in CNF
                    literals.add(literal)
            else:
                # This shouldn't happen if distribution worked correctly
                raise ValueError(f"Non-literal found within OR structure during clause collection: {f}")
        return {frozenset(literals)}  # Return a set containing one clause
    elif is_literal(formula):
        # A single literal is a clause by itself
        literal = formula_to_literal(formula)
        if literal:  # Should always be true
            return {frozenset([literal])}
        else:  # Should not happen
            raise ValueError(f"Could not convert assumed literal to literal: {formula}")
    else:
        raise TypeError(f"Unexpected formula structure during clause collection: {type(formula)}")


def to_cnf(formula: Formula) -> CNF:
    """
    Converts a given propositional logic Formula object into CNF.

    Args:
        formula: The Formula object to convert.

    Returns:
        A set of frozensets, where each frozenset represents a clause
        (a disjunction of literals) and the outer set represents the
        conjunction of these clauses. Literals are Atom or Not(Atom) objects.
        Returns an empty set {} if the formula is unsatisfiable (equivalent to False).
        Returns a set containing an empty frozenset {frozenset()} if the formula
        is a tautology (equivalent to True - often handled by removing tautological clauses).
        Note: Current _collect_clauses removes tautological clauses, so True becomes {}. Be careful.
               We might adjust this later if needed for resolution edge cases.
               Let's refine this: if the *only* result is tautology, return {frozenset()}.
    """
    if not isinstance(formula, Formula):
        raise TypeError("Input must be a Formula object.")

    # 1. Eliminate Implications (↔, →)
    no_imp = _eliminate_implications(formula)
    # print(f"DEBUG: After eliminate_implications: {no_imp}") # Optional

    # 2. Move Negations Inwards (NNF)
    nnf = _move_negation_inwards(no_imp)
    # print(f"DEBUG: After move_negation_inwards (NNF): {nnf}") # Optional

    # 3. Distribute ∨ over ∧
    distributed = _distribute_or_over_and(nnf)
    # print(f"DEBUG: After distribute_or_over_and: {distributed}") # Optional

    # 4. Collect clauses
    cnf_clauses = _collect_clauses(distributed)

    # Handle edge case: If formula is a tautology, _collect_clauses might return empty set
    # because all resulting clauses were trivial (like p V ~p).
    # Conventionally, CNF of True is an empty set of clauses.
    # If the original formula wasn't obviously False, and we get {}, it was likely True.
    # Let's stick to returning {} for True for now. Resolution handles {} result correctly.
    # We also need to handle False. If NNF resulted in contradiction like (p & ~p),
    # _distribute might yield complex forms, but _collect_clauses should handle it.
    # A direct contradiction 'p & ~p' would become And(Atom(p), Not(Atom(p))) in NNF
    # and stay that way after distribute. _collect_clauses would combine {frozenset({Atom(p)})}
    # and {frozenset({Not(Atom(p))})}. This is NOT the empty clause yet. Resolution finds that.

    return cnf_clauses


# --- Helper to print CNF nicely ---
def cnf_to_string(cnf: CNF) -> str:
    """Converts a CNF set back to a readable string."""
    if not cnf:
        return "{}"  # Represents True (empty conjunction)
    clause_strs = []
    for clause in cnf:
        if not clause:
            return "⊥"  # Represents False (empty clause)
        literal_strs = [str(lit) for lit in
                        clause]  ##orted([str(lit) for lit in clause], key=str.lower) # Sort for consistent output
        clause_strs.append("(" + " ∨ ".join(literal_strs) + ")")
    return " ∧ ".join(sorted(clause_strs))  # Sort clauses for consistent output


# --- Example Usage ---
if __name__ == "__main__":
    # Assuming formula classes and parser are defined above or imported

    print("\n--- CNF Conversion Examples ---")

    # f_simple = parse_formula("p")
    # cnf_simple = to_cnf(f_simple)
    # print(f"Formula: {f_simple}")
    # print(f"CNF: {cnf_to_string(cnf_simple)}")
    # print(f"Raw CNF: {cnf_simple}\n") # Raw representation
    #
    # f_imp = parse_formula("p → q")
    # cnf_imp = to_cnf(f_imp)
    # print(f"Formula: {f_imp}")
    # print(f"CNF: {cnf_to_string(cnf_imp)}")  # Expect: (¬p ∨ q)
    # print(f"Raw CNF: {cnf_imp}\n")
    #
    # f_iff = parse_formula("p ↔ q")
    # cnf_iff = to_cnf(f_iff)
    # print(f"Formula: {f_iff}")
    # print(f"CNF: {cnf_to_string(cnf_iff)}") # Expect: (¬p ∨ q) ∧ (p ∨ ¬q)
    # print(f"Raw CNF: {cnf_iff}\n")
    #

    # # TODO: Robert example
    # Original example from slides: r ↔ (p ∨ s)
    f_complex_str = "r <-> (p | s)"
    f_complex = parse_formula(f_complex_str)
    cnf_complex = to_cnf(f_complex)
    print(f"Formula: {f_complex_str}  -->  {f_complex}")
    print(f"CNF: {cnf_to_string(cnf_complex)}")  # Expect: (¬r ∨ p ∨ s) ∧ (¬p ∨ r) ∧ (¬s ∨ r)
    print(f"Raw CNF: {cnf_complex}\n")
    #
    # f_demorgan_str = "¬(p ∧ q)"
    # f_demorgan = parse_formula(f_demorgan_str)
    # cnf_demorgan = to_cnf(f_demorgan)
    # print(f"Formula: {f_demorgan_str}  -->  {f_demorgan}")
    # print(f"CNF: {cnf_to_string(cnf_demorgan)}")  # Expect: (¬p ∨ ¬q)
    # print(f"Raw CNF: {cnf_demorgan}\n")
    #
    # f_distrib_str = "a ∨ (b ∧ c)"
    # f_distrib = parse_formula(f_distrib_str)
    # cnf_distrib = to_cnf(f_distrib)
    # print(f"Formula: {f_distrib_str}  -->  {f_distrib}")
    # print(f"CNF: {cnf_to_string(cnf_distrib)}")  # Expect: (a ∨ b) ∧ (a ∨ c)
    # print(f"Raw CNF: {cnf_distrib}\n")
    #
    # #TODO: Tautology not working
    # f_tautology_str = "p ∨ ¬p"
    # f_tautology = parse_formula(f_tautology_str)
    # cnf_tautology = to_cnf(f_tautology)
    # print(f"Formula: {f_tautology_str}  -->  {f_tautology}")
    # print(f"CNF: {cnf_to_string(cnf_tautology)}")  # Expect: {} (True)
    # print(f"Raw CNF: {cnf_tautology}\n")
    #
    # # TODO: What the fuck is this?
    # f_contradiction_str = "p ∧ ¬p"
    # f_contradiction = parse_formula(f_contradiction_str)
    # cnf_contradiction = to_cnf(f_contradiction)
    # print(f"Formula: {f_contradiction_str}  -->  {f_contradiction}")
    # print(f"CNF: {cnf_to_string(cnf_contradiction)}")  # Expect: (p) ∧ (¬p) (Resolution will find contradiction)
    # print(f"Raw CNF: {cnf_contradiction}\n")
