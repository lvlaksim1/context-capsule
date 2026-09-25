# Current state

Context Capsule v2 remains development-only on `v2-manager-runtime`; stable `main` / v1.3.1 and known consumers are unchanged.

## IOSPM-001

`IOSPM-001` is CLOSED / Medium severity / High confidence.

Canonical final evidence is `AUD-2026-09-24-IOSPM-001-RETEST-002`. The affected iOS Project Manager adopted the fail-closed sealed-generation mechanism successfully; no new finding was introduced.

The previous working-view statement that IOSPM-001 still awaited independent retest was stale and is superseded by this canonical Auditor result.

## Runtime identity adoption

Owner-authorized `TASK-CC-RUNTIME-IDENTITY-ADOPTION-001` is active.

The governing runtime invariant is:
- one runtime carries at most one persistent Agent identity for its lifetime;
- a different persistent target requires a separate runtime;
- interactive bounded delegation uses durable manual-pull;
- autonomous caller continuation uses a dependency-bound fresh caller runtime;
- responsibility/authority semantics v2 remain unchanged;
- every user-visible Agent/infrastructure message carries the Moscow-time source header as diagnostic metadata only.

Implementation is confined to `v2-manager-runtime`.
