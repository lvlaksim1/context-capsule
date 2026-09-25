# DEC-0020 — Fixed persistent-Agent runtime identity

Status: accepted
Date: 2026-09-25

## Decision

A runtime that reinstantiates a persistent Agent is bound to that Agent identity for the lifetime of the runtime.

A different persistent target Agent always requires a separate runtime.

Interactive bounded delegation uses durable `continuation:manual-pull`: verified child output remains in GitHub and the caller retrieves it during a later Owner/caller interaction.

Autonomous bounded delegation may use `continuation:automatic-new-runtime` only through a dependency-bound `runtime:caller-continuation` task targeting the caller. The caller then resumes in a fresh runtime after verified child completion.

Historical pending same-runtime-return records remain recovery-compatible evidence only. They may be consumed by a fresh runtime bound to the recorded caller and never authorize persistent identity switching.

Every user-visible persistent-Agent or infrastructure message starts with `DD.MM.YYYY · HH:MM MSK · <source_id>` using Europe/Moscow time. This header is diagnostic and is not identity authority.

## Preserved invariants

- responsibility semantics v2;
- commitment ownership;
- authority attenuation and provenance;
- explicit handoff semantics;
- target isolation;
- execution fencing;
- direct Owner-to-Agent entry points;
- manager-state generation integrity and fail-closed recovery.

## Authority

Owner directive `OWNER-2026-09-25-RUNTIME-IDENTITY-AFFINITY`.

Implementation contract: `lvlaksim1/agent-control-plane@56bc76cba69f05cd21ed5d06c6adb264ff05a70f` and subsequent task-only commits.
