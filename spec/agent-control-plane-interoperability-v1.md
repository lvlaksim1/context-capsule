# Agent Control-Plane Interoperability v1

Status: normative development contract for optional orchestration interoperability.

## Purpose

Context Capsule persistent agents may be invoked directly by a human or through external orchestration. The orchestration layer is optional infrastructure. It does not own agent identity and it does not grant authority merely by delivering work.

This contract is transport-neutral. Core intentionally does not depend on a particular queue, scheduler, repository layout, lease service, or worker implementation.

## Invariants

1. **Direct invocation remains first-class.** Owner/requester ↔ agent interaction does not require Supervisor or a control plane.
2. **Task transport is non-escalating.** Delivery, registry membership, worker allocation, or tool access cannot increase authority.
3. **Target-side validation is mandatory.** The reinstantiated target agent validates issuer, authority provenance, target identity, scope, constraints, requested effects, and completion contract against its own mandate before acceptance.
4. **Agent-to-agent routing is allowed but bounded.** An authorized Project Manager or Service Agent may request work directly; Supervisor is not a universal routing hop.
5. **Execution fencing is conditional but strict.** If an external execution context supplies a fence, the target runtime revalidates it immediately before every consequential write and before terminal completion. Stale or unverifiable runtimes do not write.
6. **Checkpointing is resumable, not cognitive persistence.** Checkpoints contain stable task/execution facts, verified evidence, current step, and next action; never hidden chain-of-thought.
7. **Completion is evidence-backed.** Success requires the declared completion evidence, not an agent assertion.
8. **Terminal cleanup is canonical.** A terminal task cannot retain an active execution claim/fence projection.

Profiles may add stricter requirements but may not weaken these invariants.
