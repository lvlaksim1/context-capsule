# DEC-0002 — Target context remains local

- Status: active
- Date: 2026-09-20

## Decision

The full context of a repository with an installed capsule is stored in that same repository. No part of that project's context is synchronized back to Context Capsule Core.

## Consequences

- no central context registry;
- no telemetry or installation statistics;
- target repositories remain autonomous;
- private project context stays under the target repository's own access controls.
