# Manager intentions and commitments

## Completed foundational milestones

- Project Manager v2 hardening and historical audit/remediation/retest chain.
- Minimal Service Agent Base.
- Task-scoped interactive-first Core amendment; PTC-003 CLOSED / High confidence.
- Crash-safe bounded-delegation live-return Core amendment; LRC-001 CLOSED / High confidence.
- Persistent-agent taxonomy (`Agent ≠ Runtime ≠ Skill ≠ Workflow`) with Tool/Task boundaries; TAX-001 CLOSED / High confidence.
- Delegation / responsibility / authority hardening; DRA-001 and DRA-002 CLOSED / High confidence.

## Active commitments

- Preserve task-scoped interactive-first execution and unrelated autonomous scheduler availability.
- Preserve mandatory live carrier for scheduler-visible interactive work.
- Preserve durable pending caller continuation, acknowledgement-before-effects, autonomous return recovery, and explicit handoff separation.
- Preserve direct Owner operation without synthetic ACP state when there is no scheduler-visible projection.
- Keep stable `main`, v1.3.1 consumers, stable-v2 promotion, and migrations unchanged without explicit Owner authorization.
- Preserve the taxonomy boundary: execution carriers/capabilities/orchestration never become authority or responsibility holders merely through execution.

## IOSPM-001 remediation

- commitment: ENG-2026-09-24-IOSPM-001-REMEDIATION
- status: active pending independent Auditor retest
- responsibility: context-capsule-project-manager
- closure rule: do not mark IOSPM-001 CLOSED until independent Auditor retest verifies fail-closed mixed-generation behavior and legacy bootstrap semantics.
