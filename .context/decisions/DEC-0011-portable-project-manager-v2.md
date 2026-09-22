# DEC-0011 — Context Capsule v2 is a portable Project Manager

- Status: accepted for development
- Date: 2026-09-22

## Decision

Evolve Context Capsule from repository-local durable project memory into a portable Project Manager representation.

The manager has a stable runtime-independent identity, universal Core-managed operating protocol, repository-local mandate, BDI-style active state (beliefs, goals, intentions, plans), and typed semantic/episodic/procedural memory.

Runtime conversation/checkpoint state is explicitly outside durable manager identity. Handoff becomes an optional emergency summary rather than the primary continuity mechanism.

Beliefs capable of influencing future decisions must preserve provenance and authority. Major v1.3→v2 transition is explicit and cannot be hidden inside repair.

## Rationale

Research across contemporary agent frameworks and memory systems consistently separates agent definition/identity, long-term memory, runtime checkpoint state, and operational harness behavior. Persistent-memory security also requires provenance to survive consolidation.
