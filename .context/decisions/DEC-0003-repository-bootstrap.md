# DEC-0003 — Repository-based bootstrap

- Status: active
- Date: 2026-09-20

## Decision

New installations should bootstrap from the canonical `context-capsule` repository rather than by passing a ZIP archive into a fresh chat.

The bootstrap process is deterministic, version-pinned, validated, and non-destructive.
