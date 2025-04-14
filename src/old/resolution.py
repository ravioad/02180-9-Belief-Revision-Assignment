def resolve(ci, cj):
    """Try to resolve two clauses. Return resolvent(s) or None."""
    resolvents = []
    for di in ci:
        for dj in cj:
            if di == negate_literal(dj):
                new_clause = list(set(ci + cj) - {di, dj})
                resolvents.append(sorted(new_clause))
    return resolvents


def negate_literal(lit):
    """Negate a literal string."""
    return lit[1:] if lit.startswith('¬') else '¬' + lit


def entails(belief_base, query):
    """Check if the belief base entails the query using resolution."""
    # Clone belief base
    clauses = [clause[:] for clause in belief_base]

    # Add negated query to clauses
    negated_query = [['¬' + query]] if not query.startswith('¬') else [[query[1:]]]
    clauses.extend(negated_query)

    print("Extended clauses:", clauses)
    new = set()

    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]

        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            for res in resolvents:
                print(f"Resolving {ci} and {cj} => {res}")
                if res == []:
                    return True  # Empty clause = contradiction = entailment
                new.add(tuple(res))

        if all(list(r) in clauses for r in new):
            return False  # No new info, cannot derive empty clause

        for r in new:
            if list(r) not in clauses:
                clauses.append(list(r))
