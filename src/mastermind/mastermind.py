# --- M1: Configuration ---
from itertools import combinations, permutations
from typing import List, Tuple

from src.belief_base import BeliefBase
from src.belief_revision import revise
from src.formula import Atom, Or, And, Not, Formula
from src.resolution import entails_resolution

NUM_POSITIONS = 2
COLORS = [f"c{i}" for i in range(1, 4)]  # c1, c2, c3


def S(color: str, pos: int) -> Atom:
    """Helper to create secret code Atom objects consistently."""
    if color not in COLORS:
        raise ValueError(f"Invalid color: {color}")
    if not (1 <= pos <= NUM_POSITIONS):
        raise ValueError(f"Invalid position: {pos}")
    return Atom(f"S_{color}_p{pos}")


ALL_ATOMS = [S(c, p) for c in COLORS for p in range(1, NUM_POSITIONS + 1)]


def create_mastermind_initial_kb() -> BeliefBase:
    """Creates the initial KB with game rules."""
    kb = BeliefBase()
    print("--- Creating Initial Mastermind KB ---")

    # Rule 1: Each position has exactly one color
    print("Adding: Each position has exactly one color...")
    for p in range(1, NUM_POSITIONS + 1):
        # At least one color in this position
        at_least_one_list = [S(c, p) for c in COLORS]
        kb.add_belief(Or.from_list(at_least_one_list))

        # At most one color in this position
        for c1, c2 in combinations(COLORS, 2):
            kb.add_belief(Or(Not(S(c1, p)), Not(S(c2, p))))

    # Rule 2: Each color is used at most once (no duplicates in secret)
    print("Adding: Each color used at most once...")
    for c in COLORS:
        for p1, p2 in combinations(range(1, NUM_POSITIONS + 1), 2):
            kb.add_belief(Or(Not(S(c, p1)), Not(S(c, p2))))

    print(f"Initial KB created with {len(kb)} rule formulas.")
    print(f"Initial KB created with {str(kb)} rule formulas.")
    return kb


# Helper function for creating nested Ors from a list
@classmethod
def from_list(cls, formulas: List[Formula]) -> Formula:
    """Class method for Or/And to create nested structure from a list."""
    if not formulas:
        raise ValueError("Cannot create Or/And from empty list directly.")
    if len(formulas) == 1:
        return formulas[0]
    result = formulas[0]
    for i in range(1, len(formulas)):
        if cls == Or:
            result = Or(result, formulas[i])
        elif cls == And:
            result = And(result, formulas[i])
        else:
            raise TypeError("from_list only supported for And/Or")
    return result


# Add the class method to Or and And classes
Or.from_list = from_list
And.from_list = from_list


def code_to_formula(code: Tuple[str, ...]) -> Formula:
    """Converts a code tuple (e.g., ('c1','c3','c2')) into a Formula (conjunction of Atoms)."""
    if len(code) != NUM_POSITIONS:
        raise ValueError("Code length mismatch")
    atoms = []
    for i, color in enumerate(code):
        pos = i + 1
        atoms.append(S(color, pos))
    # Return conjunction of these atoms
    return And.from_list(atoms)


def calculate_feedback(secret_code: Tuple[str, ...], guess_code: Tuple[str, ...]) -> Tuple[int, int]:
    """Calculates (black_pegs, white_pegs) for a guess given a secret."""
    blacks = 0
    whites = 0
    secret_list = list(secret_code)
    guess_list = list(guess_code)
    secret_color_counts = {c: 0 for c in COLORS}
    guess_color_counts = {c: 0 for c in COLORS}

    # Calculate blacks and mark used positions/colors
    used_secret_indices = [False] * NUM_POSITIONS
    used_guess_indices = [False] * NUM_POSITIONS
    for i in range(NUM_POSITIONS):
        if guess_list[i] == secret_list[i]:
            blacks += 1
            used_secret_indices[i] = True
            used_guess_indices[i] = True
        else:
            # Count colors for white peg calculation later
            secret_color_counts[secret_list[i]] += 1
            guess_color_counts[guess_list[i]] += 1

    # Calculate whites using remaining colors/positions
    for i in range(NUM_POSITIONS):
        # Only consider positions not used for black pegs
        if not used_guess_indices[i]:
            guessed_color = guess_list[i]
            # Is this color present in the secret code (in a position not used for blacks)?
            if secret_color_counts.get(guessed_color, 0) > 0:
                whites += 1
                secret_color_counts[guessed_color] -= 1  # Consume one instance

    return blacks, whites


def generate_possible_codes() -> List[Tuple[str, ...]]:
    """Generates all valid codes (permutations of NUM_POSITIONS distinct colors)."""
    possible_codes = []
    # Get all combinations of NUM_POSITIONS colors from the available COLORS
    for color_combo in combinations(COLORS, NUM_POSITIONS):
        # Get all permutations for each combination
        for p in permutations(color_combo):
            possible_codes.append(p)
    return possible_codes


def mastermind():
    initial_kb = create_mastermind_initial_kb()
    current_kb = initial_kb  # Start with the rules

    # --- Choose a Secret Code (for simulation purposes) ---
    # In a real game, this is hidden. We use it to generate feedback.
    SECRET_CODE: Tuple[str, ...] = ('c3', 'c2')  # Example secret
    print(f"\n--- Starting Mastermind Simulation ---")
    print(f"Secret Code (for simulation): {SECRET_CODE}")

    possible_codes = generate_possible_codes()
    print(f"Total possible valid codes: {len(possible_codes)}")

    MAX_GUESSES = 10
    for guess_num in range(1, MAX_GUESSES + 1):
        print(f"\n--- Guess #{guess_num} ---")

        print("Finding consistent codes...")
        consistent_codes = []
        for potential_code_tuple in possible_codes:
            potential_code_formula = code_to_formula(potential_code_tuple)

            temp_kb_beliefs = current_kb.get_beliefs() + [potential_code_formula]
            temp_bb = BeliefBase(temp_kb_beliefs)

            if not entails_resolution(temp_bb, Atom("FALSE_ATOM")):
                consistent_codes.append(potential_code_tuple)
            else:
                print(f"  Code {potential_code_tuple} is inconsistent.")

        print(f"Found {len(consistent_codes)} consistent codes remaining.")

        if not consistent_codes:
            print("Error: No consistent codes remain! KB might be contradictory or logic error.")
            break

        current_guess_tuple = consistent_codes[0]
        print(f"Making guess: {current_guess_tuple}")

        # ** Check if won **
        if current_guess_tuple == SECRET_CODE:
            print("\n*** Correct Code Guessed! Agent Wins! ***")
            break

        blacks, whites = calculate_feedback(SECRET_CODE, current_guess_tuple)
        print(f"Feedback received: Blacks={blacks}, Whites={whites}")

        print("Generating feedback formula...")
        formulas_matching_feedback = []
        for code_tuple in possible_codes:
            b_sim, w_sim = calculate_feedback(code_tuple, current_guess_tuple)
            if b_sim == blacks and w_sim == whites:
                formulas_matching_feedback.append(code_to_formula(code_tuple))

        if not formulas_matching_feedback:
            print("Error: No possible code matches the received feedback? Impossible.")
            break

        feedback_formula = Or.from_list(formulas_matching_feedback)
        print(f"Feedback formula (simplified): Disjunction of {len(formulas_matching_feedback)} matching codes.")

        print("Revising belief base with feedback formula...")
        current_kb = revise(current_kb, feedback_formula)
        print(f"Revision complete. New KB has {len(current_kb)} explicit beliefs.")

        possible_codes = consistent_codes  # Start next search from currently consistent ones

    if guess_num == MAX_GUESSES and current_guess_tuple != SECRET_CODE:
        print("\n--- Agent failed to guess within limit. ---")
