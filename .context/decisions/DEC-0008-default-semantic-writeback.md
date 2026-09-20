# DEC-0008 — Default semantic write-back during normal work

## Status

Accepted.

## Decision

Context Capsule's default behavior requires the active AI/agent to persist significant durable project changes during normal work.

The agent must not wait for a separate owner command such as "save context" or "update the capsule", and must not defer durable semantic write-back merely until the chat ends.

This is a universal Core default, not a project-specific convention.

## Boundary

Only durable semantic changes belong in Context Capsule. Routine volatile/runtime churn remains excluded by the semantic-sync rules.
