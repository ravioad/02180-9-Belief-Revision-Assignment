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
    if not isinstance(formula, Formula):
        raise TypeError("Input must be a Formula object.")

    # 1. Eliminate Implications (↔, →)
    no_imp = _eliminate_implications(formula)

    # 2. Move Negations Inwards (NNF)
    nnf = _move_negation_inwards(no_imp)

    # 3. Distribute ∨ over ∧
    distributed = _distribute_or_over_and(nnf)

    # 4. Collect clauses
    cnf_clauses = _collect_clauses(distributed)
    return cnf_clauses


def cnf_to_string(cnf: CNF) -> str:
    """Converts a CNF set back to a readable string."""
    if not cnf:
        return "{}"
    clause_strs = []
    for clause in cnf:
        if not clause:
            return "⊥"
        literal_strs = [str(lit) for lit in clause]
        clause_strs.append("(" + " ∨ ".join(literal_strs) + ")")
    return " ∧ ".join(sorted(clause_strs))
