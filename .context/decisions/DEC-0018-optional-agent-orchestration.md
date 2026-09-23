# DEC-0018 — Optional transport-neutral agent orchestration

Status: accepted for v2 development by explicit Owner direction on 2026-09-23.

## Decision

Context Capsule Core supports direct human invocation and optional external agent orchestration as two compatible execution paths.

The orchestration contract is transport-neutral. Core defines task authority provenance, target-side mandate validation, optional supplied execution fencing, safe checkpoints, evidence-backed completion, terminal execution cleanup, and bounded agent-to-agent routing. It does not embed a particular scheduler, queue, gateway, repository path, or worker implementation.

Direct Owner ↔ agent communication remains first-class. Supervisor is not a mandatory development proxy or routing hop.

## Rationale

The live Agent Control Plane experiment proved PM→Auditor routing, deterministic dependency gating, CAS admission, stale-runtime fencing, and recovery after a pre-projection runtime loss. Those behaviors are useful generic safety invariants, while their GitHub/Scheduled-Chat implementation details are infrastructure-specific and therefore remain outside Core.

## Consequences

- Project Manager and Service Agent contracts gain the same non-escalating external-task boundary.
- Existing direct-chat operation remains valid and does not depend on a scheduler.
- Future Agent Catalog/Factory output can target the generic interoperability contract rather than a specific dispatcher implementation.
- Stable v2 promotion and consumer migration remain separately gated.
