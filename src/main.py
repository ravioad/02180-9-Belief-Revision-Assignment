from src.belief_base import BeliefBase
from src.parser import parse_formula

if __name__ == "__main__":
    clause1_str = "~r | p | s"  # Represents (¬r ∨ p ∨ s)
    clause2_str = "~p | r"  # Represents (¬p ∨ r)
    clause3_str = "~s | r"  # Represents (¬s ∨ r)
    clause1 = parse_formula(clause1_str)
    clause2 = parse_formula(clause2_str)
    clause3 = parse_formula(clause3_str)

    # Create a list of these formula objects
    beliefs_list = [clause1, clause2, clause3]  # Add extra_belief here if needed

    # Create the BeliefBase instance with these clauses
    cnf_belief_base = BeliefBase(beliefs_list)

    # Print the belief base to see the result
    print("--- Belief Base containing clauses from CNF ---")
    print(cnf_belief_base)
    print(f"Number of belief formulas: {len(cnf_belief_base)}")

    # You can retrieve the list if needed
    retrieved_beliefs = cnf_belief_base.get_beliefs()
    print("\nRetrieved belief list:")
    for belief in retrieved_beliefs:
        print(f"- {belief} (Type: {type(belief).__name__})")