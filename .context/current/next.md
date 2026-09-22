# Next actions

1. Repeat the cold-reinstantiation acceptance test from a completely new runtime and confirm it reports manager-state authority `v2-manager-runtime` and product authority `main` without conflating them.
2. Verify that the new runtime treats `authoritative_branch` only as the compatibility alias of manager-state authority and reconciles production facts against `main`.
3. Continue the acceptance suite with adversarial memory/provenance, belief supersession, commitment lifecycle, concurrent runtime reconciliation, and bounded recovery.
4. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
