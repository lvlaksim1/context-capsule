# DEC-0001 — Separate Context Capsule Core repository

- Status: active
- Date: 2026-09-20

## Decision

Context Capsule is maintained as its own central repository, independent from application projects such as `ai-agent-lab`.

The central repository contains the capsule implementation and its lifecycle rules. It is not a store for the context of repositories that use the capsule.

## Rationale

Application projects must not become accidental infrastructure dependencies for the Context Capsule mechanism.
