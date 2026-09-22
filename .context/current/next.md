# Next actions

1. Continue v2 hardening with automation-first verification; every machine-checkable invariant should become a permanent regression test.
2. Use an isolated consumer testbed only for occasional black-box behavioral smoke checks that cannot be established deterministically.
3. Resolve real semantic inconsistencies when observed; do not create write-back churn for confirming evidence alone.
4. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
5. Do not freeze v2 semantics until the remaining non-deterministic behavior has sufficient evidence.
