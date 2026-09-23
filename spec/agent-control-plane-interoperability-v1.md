# Agent Control-Plane Interoperability v1

Status: normative development contract for optional orchestration interoperability.

## Purpose

Context Capsule persistent agents may be invoked directly by a human or through external orchestration. The orchestration layer is optional infrastructure. It does not own agent identity and it does not grant authority merely by delivering work.

This contract is transport-neutral. Core intentionally does not depend on a particular queue, scheduler, repository layout, lease service, or worker implementation.

## Invariants

1. **Interactive-first execution is mandatory.** When an Owner-facing live runtime is actively carrying an authorized work chain, GitHub may store the durable handoff, but the next persistent agent is reinstantiated directly in that live runtime. Scheduled Tasks or other autonomous wake infrastructure may advance that chain only after explicit autonomous/background delegation or when no live carrier remains.
2. **Direct invocation remains first-class.** Owner/requester ↔ agent interaction does not require Supervisor or a control plane.
3. **Autonomous scheduling is fallback transport.** Scheduler availability, a queued task, wake signal, or execution slot never makes autonomous routing preferable to an active interactive carrier.
4. **Task transport is non-escalating.** Delivery, registry membership, worker allocation, or tool access cannot increase authority.
5. **Target-side validation is mandatory.** The reinstantiated target agent validates issuer, authority provenance, target identity, scope, constraints, requested effects, and completion contract against its own mandate before acceptance.
6. **Agent-to-agent routing is allowed but bounded.** An authorized Project Manager or Service Agent may request work directly; Supervisor is not a universal routing hop.
7. **Execution fencing is conditional but strict.** If an external execution context supplies a fence, the target runtime revalidates it immediately before every consequential write and before terminal completion. Stale or unverifiable runtimes do not write.
8. **Checkpointing is resumable, not cognitive persistence.** Checkpoints contain stable task/execution facts, verified evidence, current step, and next action; never hidden chain-of-thought.
9. **Completion is evidence-backed.** Success requires the declared completion evidence, not an agent assertion.
10. **Terminal cleanup is canonical.** A terminal task cannot retain an active execution claim/fence projection.

Profiles may add stricter requirements but may not weaken these invariants.
