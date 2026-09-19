# DEC-0005 — Rich stable semantics, compact working set

- Status: active
- Date: 2026-09-20

## DECISION

Context Capsule v1.2 separates stable project semantics from the current working set.

Stable project meaning lives in `project/{identity,goals,architecture,constraints}`. Current resumable work lives in `current/{state,blockers,next}` and must remain compact.

Projects with a separate volatile runtime authority such as `.agent/` keep execution churn there; only durable semantic consequences are promoted into `.context/`.

Branch topology is explicit through `authoritative_branch`, `discovery_branch`, and `branch_mode`.

## Rationale

This combines the strongest observed patterns from the legacy capsules: the structured semantics and evidence discipline of `fgis-fsa-il`, the concise project-specific recovery of `telegram-receiver`, and the `.context`/`.agent` separation plus branch redirect used by `ai-agent-lab`.
