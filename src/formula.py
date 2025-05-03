import re
from typing import List


class Formula:
    """Base (Parent) class for all propositional logic formulas."""
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        raise NotImplementedError

    def get_atoms(self) -> set:
        """Returns a set of all atomic variable names in the formula."""
        raise NotImplementedError


class Atom(Formula):
    """Represents an atomic proposition (variable)."""
    def __init__(self, name: str):
        # Basic validation: starts with letter, alphanumeric afterwards
        if not name or not name[0].isalpha() or not name.replace('_', '').isalnum():
             raise ValueError(f"Invalid atom name: '{name}'. Must start with a letter and be alphanumeric (underscores allowed).")
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def get_atoms(self) -> set:
        return {self.name}



class Not(Formula):
    """Represents negation (¬)."""
    def __init__(self, operand: Formula):
        if not isinstance(operand, Formula):
            raise TypeError("Operand for Not must be a Formula")
        self.operand = operand

    def __str__(self):
        # Add parentheses if the operand is a binary operation
        op_str = str(self.operand)
        if isinstance(self.operand, BinaryOp):
             return f"¬({op_str})"
        return f"¬{op_str}"


    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("¬", self.operand))

    def get_atoms(self) -> set:
        return self.operand.get_atoms()



class BinaryOp(Formula):
    """Base class for binary connectives (And, Or, Implies, Iff)."""
    # Precedence levels (lower binds tighter)
    PRECEDENCE = { '¬': 0, '∧': 1, '∨': 2, '→': 3, '↔': 4 }

    def __init__(self, left: Formula, right: Formula, symbol: str):
        if not isinstance(left, Formula) or not isinstance(right, Formula):
            raise TypeError("Operands for BinaryOp must be Formulas")
        self.left = left
        self.right = right
        self.symbol = symbol # e.g., "∧", "∨", "→", "↔"

    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        current_prec = BinaryOp.PRECEDENCE[self.symbol]

        # Parenthesize left operand if necessary
        if isinstance(self.left, BinaryOp):
            left_prec = BinaryOp.PRECEDENCE.get(self.left.symbol, -1)
            # Add parens if inner operator has lower precedence (higher number)
            if left_prec > current_prec:
                left_str = f"({left_str})"

        # Parenthesize right operand if necessary
        if isinstance(self.right, BinaryOp):
            right_prec = BinaryOp.PRECEDENCE.get(self.right.symbol, -1)
            # Add parens if inner operator has lower precedence (higher number)
            if right_prec > current_prec:
                right_str = f"({right_str})"
            # Add parens if same precedence AND current operator is right-associative (like ->)
            # This handles cases like a -> (b -> c) correctly.
            elif right_prec == current_prec and self.symbol == '→':
                right_str = f"({right_str})"
            # Add parens if same precedence AND current op is left-assoc (optional but good practice)
            # This ensures a OP (b OP c) prints correctly if OP is left assoc.
            elif right_prec == current_prec and self.symbol != '→':  # Assuming others are left-assoc
                right_str = f"({right_str})"

        return f"{left_str} {self.symbol} {right_str}"


    def __eq__(self, other):
        # Check if it's the same binary operation type and operands are equal
        return isinstance(other, type(self)) and \
               self.left == other.left and \
               self.right == other.right

    def __hash__(self):
        return hash((self.symbol, self.left, self.right))

    def get_atoms(self) -> set:
        return self.left.get_atoms().union(self.right.get_atoms())


class And(BinaryOp):
    """Represents conjunction (∧)."""
    def __init__(self, left: Formula, right: Formula):
        super().__init__(left, right, "∧")

class Or(BinaryOp):
    """Represents disjunction (∨)."""
    def __init__(self, left: Formula, right: Formula):
        super().__init__(left, right, "∨")

class Implies(BinaryOp):
    """Represents implication (→)."""
    def __init__(self, left: Formula, right: Formula):
        super().__init__(left, right, "→")

class Iff(BinaryOp):
    """Represents biconditional (↔)."""
    def __init__(self, left: Formula, right: Formula):
        super().__init__(left, right, "↔")


# Operator precedence levels (lower number binds tighter)
PRECEDENCE = {'¬': 0, '∧': 1, '∨': 2, '→': 3, '↔': 4}
OPERATORS = {'¬', '∧', '∨', '→', '↔'}
BINARY_OPERATORS = {'∧', '∨', '→', '↔'}


def tokenize(formula_str: str) -> List[str]:
    """Basic tokenizer splitting on spaces and handling parentheses/negation."""
    formula_str = formula_str.replace('~', '¬')
    formula_str = formula_str.replace('&', '∧')
    formula_str = formula_str.replace('|', '∨')
    formula_str = formula_str.replace('<->', '↔')
    formula_str = formula_str.replace('->', '→')

    # Add spaces around operators and parentheses for splitting
    # Ensure single character ops and multi-char ops are handled
    formula_str = re.sub(r'([()¬∧∨→↔])', r' \1 ', formula_str)
    tokens = formula_str.strip().split()
    return [tok for tok in tokens if tok] # Filter out empty strings