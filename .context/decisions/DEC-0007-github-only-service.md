# DEC-0007 — GitHub-only service boundary

- Status: active
- Date: 2026-09-20
- Source: explicit user correction during v1.3 hardening.

## Decision

Context Capsule is a service that operates exclusively inside GitHub.

Target repositories store durable project context and lightweight discovery instructions only. They do **not** receive or execute a Context Capsule runtime, bundled Python modules, bundled schemas, desktop helpers, installers, daemons or platform-specific compatibility code.

All installation, validation, migration, repair, indexing, readiness checks and other Context Capsule mechanics are executed by the central `lvlaksim1/context-capsule` implementation through GitHub automation against repository contents/checkouts.

The user's computer is not a supported execution environment for Context Capsule and must not require Python, Windows/Linux compatibility work, local locking, local crash journals or any other local service component.

## Consequences

- CI targets the actual GitHub execution environment rather than a desktop OS compatibility matrix.
- One pinned Python version in the GitHub runner is sufficient unless the service runtime itself changes.
- `.context/tools/**` is not part of the installed capsule.
- Managed integrity applies to discovery/bootstrap text owned by Core, not copied executable runtime.
- GitHub branch/HEAD/CAS and commit publication semantics are the concurrency boundary.
- The central code may use an ephemeral GitHub runner checkout internally; that is an implementation detail, not a user-facing runtime.
- Existing legacy migration support remains temporary until the three known old capsules are migrated and verified.
