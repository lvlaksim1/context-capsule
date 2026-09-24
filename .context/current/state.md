# Current state

Context Capsule v2 remains development-only on `v2-manager-runtime`; stable `main` / v1.3.1 and known consumers are unchanged.

## IOSPM-001 remediation

Owner-authorized systemic remediation is implemented in the v2 Core development line.

The new coherence mechanism seals semantically coupled Project Manager state as one generation using the Git blob identities of:
- manager beliefs;
- manager goals;
- manager intentions;
- manager plans;
- current state;
- blockers;
- next actions;
- latest handoff.

For a protected capsule, `READY` and `recover` fail closed when any coupled file no longer matches the sealed generation. Explicit repair bootstraps protection for legacy-unsealed v2 capsules, while repair refuses to auto-seal an already-protected mismatching snapshot.

Implementation verification is green. IOSPM-001 is **remediated but not closed** pending independent Auditor retest.
