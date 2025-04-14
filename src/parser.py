from typing import List, Optional

from formula import Formula, Not, Atom, PRECEDENCE, BINARY_OPERATORS, And, Or, Implies, Iff, tokenize


class Parser:
    """Encapsulates the parsing state."""

    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[str]:
        """Return the next token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> str:
        """Consume and return the next token."""
        token = self.peek()
        if token is None:
            raise ValueError("Parse error: Unexpected end of input")
        self.pos += 1
        return token

    def parse_atom_or_paren(self) -> Formula:
        """Parses the highest precedence items: atoms or parenthesized expressions."""
        token = self.peek()

        if token == '(':
            self.consume()  # Consume '('
            expr = self.parse_expression()  # Parse the inner expression
            next_token = self.peek()
            if next_token != ')':
                raise ValueError(f"Parse error: Expected ')' but got '{next_token}' or end of input")
            self.consume()  # Consume ')'
            return expr
        elif token == '¬':
            self.consume()  # Consume '¬'
            operand = self.parse_atom_or_paren()  # Negation binds tightest to the next unit
            return Not(operand)
        elif token and token[0].isalpha() and token.replace('_', '').isalnum():
            self.consume()  # Consume atom
            return Atom(token)
        else:
            raise ValueError(f"Parse error: Expected atom, '¬', or '(' but got '{token}'")

    def parse_binary_op(self, current_precedence: int) -> Formula:
        """Parses binary operations with precedence climbing."""
        # Base case: Parse the highest precedence items first (atoms, negations, parens)
        if current_precedence > max(PRECEDENCE.values()):
            return self.parse_atom_or_paren()

        # Recursively parse the left operand with the next higher precedence
        left_operand = self.parse_binary_op(current_precedence + 1)

        # Check for operators at the current precedence level
        while True:
            op_token = self.peek()
            # Stop if no more tokens or token is not a binary operator at current precedence
            if op_token is None or op_token not in BINARY_OPERATORS or PRECEDENCE[op_token] != current_precedence:
                break

            self.consume()  # Consume the operator

            # If the operator is right-associative, parse the right operand with the *same* precedence.
            # Otherwise (left-associative), parse with the *next higher* precedence.
            # Here, we treat -> as right-associative, others as left-associative.
            if op_token == '→':
                right_operand = self.parse_binary_op(current_precedence)
            else:
                right_operand = self.parse_binary_op(current_precedence + 1)
            # <--- End special handling --->

            # Build the formula
            if op_token == '∧':
                left_operand = And(left_operand, right_operand)
            elif op_token == '∨':
                left_operand = Or(left_operand, right_operand)
            elif op_token == '→':
                left_operand = Implies(left_operand, right_operand)
            elif op_token == '↔':
                # Iff is tricky, often non-associative or lowest precedence
                # For simplicity here, treat as left-associative like others.
                left_operand = Iff(left_operand, right_operand)

        return left_operand

    def parse_expression(self) -> Formula:
        """Starts parsing an expression from the lowest precedence level."""
        # Start parsing with the lowest precedence level for binary operators (like, ↔)
        # Note: Precedence climbing handles unary negation within parse_atom_or_paren
        lowest_binary_precedence = min(PRECEDENCE[op] for op in BINARY_OPERATORS)
        return self.parse_binary_op(lowest_binary_precedence)


def parse_formula(formula_str: str) -> Formula:
    """Top-level function to parse a formula string."""
    tokens = tokenize(formula_str)
    if not tokens:
        raise ValueError("Cannot parse empty string")
    parser = Parser(tokens)
    formula = parser.parse_expression()
    # Check if all tokens were consumed
    if parser.peek() is not None:
        raise ValueError(f"Parse error: Unexpected tokens remaining: {parser.tokens[parser.pos:]}")
    return formula
