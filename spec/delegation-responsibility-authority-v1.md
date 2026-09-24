# Delegation, responsibility, and authority semantics v1

Status: normative v2 development invariant for Master Plan 8.8.

## Purpose

This specification hardens agent-to-agent work transfer beyond transport and live-return mechanics.

The central invariant is:

`responsibility ≠ authority ≠ execution ownership`.

A task may move between execution carriers or agents without silently changing commitment ownership or authority. A responsibility transfer may occur without transferring broad authority. Authority may be delegated without transferring the caller's persistent responsibility.

## 1. Four distinct concepts

### Commitment responsibility

The persistent Agent that remains answerable for satisfying an accepted commitment.

### Execution responsibility

The Agent currently asked to perform a bounded part of the work.

### Authority

The permission to perform particular effects against a target, derived from authoritative provenance and bounded by mandate/rules.

### Execution ownership

A runtime/lease/carrier/fence that decides which execution instance may act now. It is concurrency control, not responsibility or authority.

None of these concepts may be inferred from another.

## 2. Effective authority

For an agent-issued task, effective authority is the **intersection**, never the union, of:

1. the root authority provenance;
2. the caller's own effective authority;
3. the immediate task grant;
4. the callee's mandate;
5. the target's governing rules / approval gates;
6. the task scope and constraints.

If any required authority element is absent, stale, conflicting, or unverifiable, consequential action fails closed.

Task delivery, registry membership, routing, tool access, execution success, or confidence cannot increase effective authority.

## 3. Bounded delegation

Bounded delegation means:

- the caller remains the current commitment owner;
- the callee accepts only bounded execution responsibility;
- the caller remains the return target;
- no project/client ownership transfers;
- only explicitly bounded authority needed for the delegated work may be granted;
- completion returns evidence/results to the caller, which remains responsible for integration.

A bounded delegation cannot set the callee as commitment owner.

## 4. Explicit handoff

An explicit handoff is a **proposed responsibility transfer**, not an already-completed transfer.

The immutable handoff request must identify:

- the caller/current commitment owner;
- the proposed next commitment owner (the target Agent);
- the authority provenance for requesting the transfer;
- the bounded authority available for the work;
- that target acceptance is required.

The current owner remains responsible until the target Agent explicitly accepts the handoff in its own durable state.

Only after acceptance does the target become the active commitment owner.

An explicit handoff has no automatic return to the previous owner.

Responsibility transfer does **not** transfer unrestricted authority. The target still acts only within its mandate and the explicit effective authority grant.

## 5. Hardened responsibility envelope

New executable agent-to-agent tasks use responsibility semantics version 2.

The envelope distinguishes:

- `caller_agent_id`;
- `commitment_owner_agent_id` — current owner at request time;
- `proposed_commitment_owner_agent_id` — target only for explicit handoff;
- `return_to_agent_id`;
- `transfer_requires_target_acceptance`;
- `authority_chain`.

Historical version-1 responsibility artifacts may remain readable for audit/provenance, but they are not the contract for newly admitted agent-to-agent execution.

## 6. Authority chain

The authority chain preserves:

- root authority `kind + reference`;
- immediate grantor Agent;
- grant reference;
- delegation depth;
- parent task when represented;
- normalized allowed effects;
- normalized forbidden effects;
- whether further subdelegation is forbidden or only bounded.

The root authority must remain unchanged across a nested delegation chain.

The immediate grantor must be the task issuer.

## 7. Attenuation rule

For every nested subdelegation:

- child `allowed_effects` MUST be a subset of the parent's allowed effects;
- child `forbidden_effects` MUST be a superset of the parent's forbidden effects;
- inherited task constraints MUST remain present;
- delegation depth MUST increase monotonically;
- a parent marked `subdelegation = forbidden` cannot produce an executable child delegation.

A downstream agent may narrow authority further.

It may never widen it.

## 8. Target validation and acceptance

The target persistent Agent independently validates:

- issuer identity;
- root and immediate authority provenance;
- caller/current commitment owner;
- task objective/scope/constraints;
- allowed and forbidden effects;
- its own mandate;
- target rules/gates;
- responsibility mode.

Claiming a task, receiving a message, or possessing tools is not target acceptance of an explicit handoff.

Handoff acceptance is a durable Agent-state transition.

## 9. Result boundary

A result reports what was done and what evidence was produced.

A successful result:

- does not retroactively authorize an unauthorized action;
- does not expand the grant for follow-on work;
- does not transfer commitment ownership;
- does not relax inherited constraints.

Any follow-on delegation/handoff requires its own valid immutable contract.

## 10. Direct Owner invocation

Direct Owner → Agent work remains first-class.

This specification does not require synthetic agent-to-agent responsibility metadata for a direct Owner task.

If an Agent later delegates part of that Owner-derived work, the first agent-to-agent child must construct the hardened authority chain from the authoritative Owner grant that the caller actually holds.

## 11. Compatibility boundary

Historical completed tasks using the earlier responsibility shape remain readable as evidence.

Newly admitted agent-to-agent execution must use the hardened semantics.

No historical artifact is rewritten merely to satisfy the new contract.

## 12. Out of scope

This stage does not create:

- Agent Catalog;
- Agent Factory;
- item 20;
- Fast Resume / `resume.json`;
- a new central authority server;
- new project ownership rules.

It only makes delegation, responsibility, and authority semantics explicit and enforceable.
