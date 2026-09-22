# DEC-0010 — Canonical v1.3.1 provenance

## Decision

Release Context Capsule Core v1.3.1 as a provenance-hardening patch.

v1.3.0 is historical and may refer to more than one Core implementation. Starting with v1.3.1, an installed capsule is identified by both the semantic version and the exact immutable `core_commit`.

All known installed consumers must be refreshed to the same v1.3.1 canonical Core commit. Project-owned semantic context is preserved; only Core-managed surfaces and provenance metadata may change.

## Release discipline

Behavior-changing Core work must not continue under an already-published version number. Create a new patch or minor version before treating the new implementation as a stable installation source.

Canonical Core commit: `2ef41a5ed57ae514cc5980065560d7e55d5e4b9a`.
