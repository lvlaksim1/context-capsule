<!-- context-capsule:begin -->
## Context Capsule — managed agent bootstrap

Before substantial work, restore repository context from `.context/ENTRYPOINT.md`.

Use `.context/manifest.json` to locate the authoritative branch, stable project semantics, current working set, rules, decisions and runtime authorities. Reconcile stored context with current repository/CI/runtime evidence before treating it as current fact.

When `.context/tools/capsule_runtime.py` is present, its `check --ready` command is the repository-local structural/readiness check and `resume` builds a bounded recovery pack.

Persist semantic changes during work; do not copy routine heartbeats, queue churn or transient CI state into durable context. Never send target-project context back to Context Capsule Core.
<!-- context-capsule:end -->
