# Next actions

1. Run GitHub-hosted CI for the split manager-state/product-authority model and verify self VALID, READY, and reinstantiation recovery.
2. Repeat the cold-reinstantiation acceptance test from a new runtime and confirm it reports `manager_state_branch=v2-manager-runtime` and `product_branch=main` without conflating them.
3. Continue the acceptance suite with adversarial memory/provenance, belief supersession, commitment lifecycle, concurrent runtime reconciliation, and bounded recovery.
4. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
