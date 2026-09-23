# Latest handoff

Persistent manager: `context-capsule-project-manager`.
Manager-state branch: `v2-manager-runtime`.
Product authority branch: `main`.

Owner-directed pre-scaling Core work is active for automatic live delegation return.

Required semantics:
- bounded delegation keeps commitment/responsibility/authority with the caller;
- the live child task records the caller as return target;
- after verified terminal child completion, the caller is reinstantiated immediately in the same live runtime and continues from the durable result without a new Owner message;
- explicit handoff is a separate authorized responsibility transfer and has no implicit return;
- nested bounded delegations unwind one caller at a time.

Canonical Core provenance remains exclusively in `.context/capsule.json.core_commit`.

Next gate: hosted Core verification, then independent Auditor acceptance. Catalog/Factory work remains inactive.
