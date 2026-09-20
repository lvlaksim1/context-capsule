<!-- context-capsule:begin -->
## Context Capsule — managed agent bootstrap

Before substantial work, restore repository context from `.context/ENTRYPOINT.md`.

Use `.context/manifest.json` to locate the authoritative branch, stable project semantics, current working set, rules, decisions and declared runtime authorities. Reconcile stored context with current GitHub repository/CI/runtime evidence before treating it as current fact.

All Context Capsule installation, validation, migration, repair and readiness operations are performed by the central GitHub service. Do not expect or require a local Capsule runtime.

Persist semantic changes during work; do not copy routine heartbeats, queue churn or transient CI state into durable context. Never send target-project context back to Context Capsule Core.
<!-- context-capsule:end -->
