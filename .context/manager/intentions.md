# Manager intentions and commitments

## Completed foundational milestones

- Project Manager v2 hardening and historical audit/remediation/retest chain.
- Minimal Service Agent Base.
- Task-scoped interactive-first Core amendment; PTC-003 CLOSED / High confidence.
- Crash-safe bounded-delegation live-return Core amendment; LRC-001 CLOSED / High confidence.
- Persistent-agent taxonomy (`Agent ≠ Runtime ≠ Skill ≠ Workflow`) with Tool/Task boundaries; TAX-001 CLOSED / High confidence.
- Delegation / responsibility / authority hardening; DRA-001 and DRA-002 CLOSED / High confidence.
- IOSPM-001 fail-closed generation-integrity remediation and affected-manager adoption; IOSPM-001 CLOSED / Medium / High confidence.

## Active commitments

- Preserve task-scoped interactive-first execution and unrelated autonomous scheduler availability.
- Preserve mandatory live carrier for scheduler-visible interactive work.
- Preserve bounded-delegation responsibility semantics while enforcing fixed persistent-Agent runtime identity, manual-pull interactive continuation, fresh-runtime autonomous continuation, and explicit handoff separation.
- Adopt fixed persistent-Agent runtime identity systemically in Context Capsule v2 under `TASK-CC-RUNTIME-IDENTITY-ADOPTION-001`.
- Preserve direct Owner operation without synthetic ACP state when there is no scheduler-visible projection.
- Keep stable `main`, v1.3.1 consumers, stable-v2 promotion, and migrations unchanged without explicit Owner authorization.
- Preserve the taxonomy boundary: execution carriers/capabilities/orchestration never become authority or responsibility holders merely through execution.

## Runtime identity adoption

- commitment: TASK-CC-RUNTIME-IDENTITY-ADOPTION-001
- status: active
- responsibility: context-capsule-project-manager
- constraints: `runtime:separate-target`, `continuation:manual-pull`, development branch only
- closure rule: implementation and deterministic tests must pass before completion is claimed.
