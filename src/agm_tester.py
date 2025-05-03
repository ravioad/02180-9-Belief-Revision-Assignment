from belief_base import BeliefBase
from belief_revision import revise, expand
from formula import Atom, Formula, Not, Iff, Implies, Or, And
from resolution import entails_resolution

FALSE_ATOM = Atom("AGM_FALSE_CONST")


def check_success(kb: BeliefBase, phi: Formula):
    print(f"\n--- Testing Success: KB={{{', '.join(map(str, kb.get_beliefs()))}}}, phi=({phi}) ---")
    revised_kb = revise(kb, phi)
    result = entails_resolution(revised_kb, phi)
    print(f"  Result (KB * phi |= phi): {'PASS' if result else 'FAIL'}")


def check_inclusion(kb: BeliefBase, phi: Formula):
    print(f"\n--- Testing Inclusion: KB={{{', '.join(map(str, kb.get_beliefs()))}}}, phi=({phi}) ---")
    revised_kb = revise(kb, phi)
    expanded_kb = expand(kb, phi)

    all_entailed = True
    if not revised_kb.get_beliefs():
        all_entailed = True
    else:
        for f_revised in revised_kb.get_beliefs():
            if not entails_resolution(expanded_kb, f_revised):
                all_entailed = False
                break
    print(f"  Result (All revised base formulas entailed by expansion): {'PASS' if all_entailed else 'FAIL'}")


def check_vacuity(kb: BeliefBase, phi: Formula):
    print(f"\n--- Testing Vacuity: KB={{{', '.join(map(str, kb.get_beliefs()))}}}, phi=({phi}) ---")
    neg_phi = Not(phi)
    condition = not entails_resolution(kb, neg_phi)
    print(f"  Condition (KB does not entail {neg_phi}): {condition}")

    if condition:
        revised_kb = revise(kb, phi)
        expanded_kb = expand(kb, phi)
        result = (revised_kb == expanded_kb)
        print(f"  Result (Condition true -> Revised KB == Expanded KB): {'PASS' if result else 'FAIL'}")
    else:
        print("  Result (Condition false -> Postulate vacuously satisfied): PASS")


def check_consistency(kb: BeliefBase, phi: Formula):
    print(f"\n--- Testing Consistency: KB={{{', '.join(map(str, kb.get_beliefs()))}}}, phi=({phi}) ---")
    phi_consistent = not entails_resolution(BeliefBase(), Not(phi))
    print(f"  Condition (phi is consistent): {phi_consistent}")

    if phi_consistent:
        revised_kb = revise(kb, phi)
        result = not entails_resolution(revised_kb, FALSE_ATOM)
        print(f"  Result (Condition true -> Revised KB is consistent): {'PASS' if result else 'FAIL'}")
    else:
        print("  Result (Condition false -> Postulate vacuously satisfied): PASS")


def check_extensionality(kb: BeliefBase, phi: Formula, psi: Formula):
    print(f"\n--- Testing Extensionality: KB={{{', '.join(map(str, kb.get_beliefs()))}}}, phi=({phi}), psi=({psi}) ---")
    equiv_formula = Iff(phi, psi)
    condition = entails_resolution(BeliefBase(), equiv_formula)
    print(f"  Condition ({equiv_formula} is tautology): {condition}")

    if condition:
        revised_kb_phi = revise(kb, phi)
        revised_kb_psi = revise(kb, psi)
        result = (revised_kb_phi == revised_kb_psi)
        print(f"  Result (Condition true -> Revisions are equal): {'PASS' if result else 'FAIL'}")
    else:
        print("  Result (Condition false -> Postulate vacuously satisfied): PASS")


def test_agm_postulates():
    print("\n--- Running AGM Postulate Tests ---")

    p = Atom("p")
    q = Atom("q")
    not_p = Not(p)
    not_q = Not(q)
    p_implies_q = Implies(p, q)
    p_and_not_p = And(p, not_p)  # Inconsistent formula

    kb_simple = BeliefBase([p])
    kb_modus = BeliefBase([p, p_implies_q])
    kb_contra = BeliefBase([p_implies_q, not_q])  # Entails not_p

    # --- Test Success ---
    check_success(kb_simple, q)
    check_success(kb_modus, not_q)  # Requires revision

    # --- Test Inclusion ---
    # Note: Using simplified check: (KB * phi).beliefs subset (KB + phi).beliefs
    check_inclusion(kb_simple, q)
    check_inclusion(kb_modus, not_q)

    # --- Test Vacuity ---
    check_vacuity(kb_simple, q)  # ¬q not entailed by {p} -> Vacuity applies
    check_vacuity(kb_modus, q)  # ¬q not entailed by {p, p->q} -> Vacuity applies
    check_vacuity(kb_contra, p)  # ¬p *is* entailed by {p->q, ¬q} -> Vacuity does NOT apply

    # --- Test Consistency ---
    check_consistency(kb_simple, q)  # q is consistent
    check_consistency(kb_modus, not_q)  # not_q is consistent
    check_consistency(kb_simple, p_and_not_p)  # p & ¬p is inconsistent
    #
    # # --- Test Extensionality ---
    q_equiv1 = q
    q_equiv2 = Or(q, q)  # q V q is equivalent to q
    q_equiv3 = Or(q, p_and_not_p)  # q V (p & ¬p) is equivalent to q
    check_extensionality(kb_simple, q_equiv1, q_equiv2)
    check_extensionality(kb_simple, q_equiv1, q_equiv3)
    check_extensionality(kb_simple, q_equiv1, p)  # Should not apply

    print("\n--- AGM Postulate Testing Complete ---")
