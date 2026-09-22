# DEC-0014 — Normative Project Manager v2 Contract

## Decision

Context Capsule v2 installs a Core-managed normative Project Manager Contract at `.context/manager/CONTRACT.md`.

The Contract defines the behavioral invariants of the persistent Project Manager. The universal Manager Protocol operationalizes the Contract. Project-specific mandates may narrow autonomous authority but may not silently weaken universal continuity, provenance, owner-authority, memory-safety, or self-modification boundaries.

The Contract is mandatory recovery state.

## Why

The pre-contract design encoded manager behavior across Protocol, specifications, tests, and project-specific state. A separate Contract creates one public product boundary and allows structural regression tests without embedding concrete black-box scenarios into manager-readable history.

## Key invariants

- explicit owner-message semantics;
- explicit commitment lifecycle;
- durable-memory admission/retrieval/revalidation lifecycle;
- risk-scoped reconciliation before consequential action;
- prohibition on unilateral self-expansion of authority;
- external expertise does not imply project authority;
- recovery carries the Contract together with active manager state.

## Compatibility

Stable v1.3.1 is unaffected. v2 remains development-only until separately authorized for stable release and consumer migration.
