# Next actions

1. Repeat cold reinstantiation in a completely new runtime and verify it distinguishes real supersession from newer confirming evidence.
2. Confirm that a later successful CI run does not cause the manager to label state/handoff stale merely because the run ID is newer.
3. Continue the acceptance suite with adversarial memory/provenance, explicit belief supersession, commitment completion/cancellation/invalidation, concurrent-runtime reconciliation, and bounded recovery.
4. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
