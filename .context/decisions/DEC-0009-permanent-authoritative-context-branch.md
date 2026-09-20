# DEC-0009 — Permanent authoritative context branch

## Status

Accepted.

## Decision

Projects that routinely use temporary feature branches should keep Context Capsule authority on one permanent branch. The default branch is a discovery-only gateway and disposable feature branches never become semantic authority.

## Rationale

Durable project memory must not inherit the lifecycle of a temporary PR branch. A permanent authority removes merge-time branch handoff, stale closed-branch pointers, and ambiguity for fresh-chat recovery.

## Publication order

Publish and validate the authoritative context branch first. Only then publish the discovery redirect on the default branch. Each branch uses expected-parent atomic publication.
