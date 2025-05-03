# 02180 Introduction to Artificial Intelligence - Belief Revision Assignment

**Group Members:**

*   Ravi Kumar (s242513)
*   Zohair Khan (s242544)
*   David Hansen (s224349)
*   Arjaco Kaki (s232585)

## Project Overview

This project implements a belief revision engine based on the concepts discussed in the 02180 Introduction to AI course. It follows the "Belief Base" approach, using Partial Meet Contraction with a priority order (based on insertion) and the Levi Identity for revision. The core logic, including formula parsing, CNF conversion, and resolution-based entailment checking, was implemented from scratch as required. An optional Mastermind code-breaking agent using this engine was also attempted.

## File Structure
The project code is organized as follows within the submitted `src` directory:

*   **`src/__init__.py`**: Marks `src` as a Python package.
*   **`src/formula.py`**: Contains the core classes for representing propositional formulas (`Formula`, `Atom`, `Not`, `And`, `Or`, `Implies`, `Iff`).
*   **`src/parser.py`**: Implements the function (`parse_formula`) to convert string representations into `Formula` objects.
*   **`src/logic_utils.py`**: Includes utility functions for logical operations, primarily the `to_cnf` function for CNF conversion.
*   **`src/resolution.py`**: Implements the resolution rule (`resolve`) and the resolution-based entailment checking algorithm (`entails_resolution`).
*   **`src/belief_base.py`**: Defines the `BeliefBase` class to store the agent's beliefs.
*   **`src/belief_revision.py`**: Contains the implementations for `contract_partial_meet_priority`, `expand`, and `revise`.
*   **`src/agm_tester.py`**: Includes the functions (`check_success`, `check_vacuity`, etc.) used to test the implemented revision operator against AGM postulates.
*   **`src/main.py`**: The main script used to run demonstrations, examples, and tests for the core belief revision engine and potentially the simplified Mastermind run.
*   **`src/mastermind/`** (Optional Subdirectory):
    *   **`src/mastermind/__init__.py`**: Marks `mastermind` as a Python sub-package.
    *   **`src/mastermind/mastermind.py`**: Contains the code specific to the Mastermind agent attempt, including rule generation, feedback processing, and the game loop logic.

## How to Run

1.  **Navigate:** Open a terminal or command prompt and navigate to the root directory of the unzipped project (the directory containing the `src/` folder and this `README.md`).
2.  **Examine `src/main.py`:** Open the `src/main.py` file. Inside the `if __name__ == "__main__":` block, you will find several function calls, most of which are commented out (`#`). These calls demonstrate different parts of the implemented system:
    *   `test_resolution()` : tests for entailment resolution.
    *   `test_belief_revision_contraction()` : tests for partial meet contraction.
    *   `test_belief_base_revision()` : tests for belief base revision.
    *   `test_agm_postulates()` : AGM Postulates tests.
    *   `mastermind()` : The simplified Mastermind simulation.
3.  **Select Test:** Uncomment the specific function call corresponding to the functionality you wish to run or test. By default, usually only the AGM postulate tests or a basic demonstration might be uncommented.
4.  **Execute:** Run the main script using Python 3.

    ```bash
    python src/main.py
    ```
5.  **Observe Output:** The script will execute only the uncommented function calls, printing the relevant steps, results, and PASS/FAIL statuses to the console. For example, running with only `test_agm_postulates()` uncommented will show the output of the AGM verification tests. Running with `mastermind()` uncommented will attempt the (slow) simplified Mastermind simulation.
---
**If you have any questions or need help with installation, please feel free to contact me at [s242513@dtu.dk].**
