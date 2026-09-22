# Manager plans

## Completed implementation stage

1. Implement schema v4, Manager Protocol, manager identity/mandate/BDI state, typed memory, and explicit v1.3→v2 upgrade.
2. Add continuity, provenance, checkpoint-boundary, repair-boundary, and redirect-topology regression tests.
3. Make Context Capsule Core's own capsule v2-ready on the development branch.
4. Run local tests and self VALID/READY/recover checks.
5. Publish the feature-branch implementation and verify it with GitHub-hosted CI.

## Next stage

1. Review the Project Manager model against real project-management scenarios and adversarial memory cases.
2. Add regression coverage for belief supersession, provenance trust boundaries, commitment completion/cancellation, and bounded long-term-memory retrieval.
3. Freeze the v2 semantics only after that review.
4. Do not release or migrate consumers until explicitly authorized.
