# DEC-0015 — Minimal Service Agent Base

## Decision

Introduce a second Context Capsule persistent-agent archetype: **Service Agent**.

A Service Agent has a permanent home repository, professional identity, mandate, bounded authority, active service commitments, and professional memory. External repositories/projects are handled through explicit engagements and do not become the agent's owned project state.

The initial base profile is version `1.0.0-dev` and is implemented in parallel with, not as a replacement for, Project Manager v2.

## Required boundaries

- stable runtime-independent `agent_id`;
- explicit role and specialization;
- explicit requester/target/scope/authority/deliverable per engagement;
- advisory-by-default output;
- explicit grant for target-side action;
- target context isolation;
- professional-memory-only durability;
- transport does not upgrade authority;
- no unilateral self-expansion of authority;
- active engagements survive runtime replacement.

## Intended profiles

Supervisor, Auditor, Specialist Agent, and Agent Factory extend this base.

## Deferred

Do not create a universal all-agent Core yet. First exercise this base through real profiles, beginning with Supervisor.
