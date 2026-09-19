# Context Capsule entrypoint

## Recovery protocol

1. Read `.context/capsule.json` to identify the installed Context Capsule version.
2. Read `.context/manifest.json`; it is the navigation index for the actual project-context paths and authoritative branch.
3. Read the manifest-referenced project rules.
4. Read the manifest-referenced current state.
5. Read the latest handoff.
6. Read relevant durable decisions.
7. Read dialogue evidence only when the reasoning or observed chronology matters.
8. Read deeper history only when needed.
9. Verify the recovered state against the live repository at the current authoritative branch/commit, including relevant CI/workflows/runtime evidence.
10. If repository facts are newer than the capsule, repository facts win; update the capsule before substantial work continues.

## Context semantics

Use these record types when writing durable context:

- **FACT** — verified observation.
- **DECISION** — accepted architectural or implementation choice.
- **REQUIREMENT** — behavior or invariant that must hold.
- **RULE** — durable operating rule for the project.
- **PREFERENCE** — user preference that materially affects implementation.
- **HYPOTHESIS** — unverified explanation.
- **BLOCKER** — condition preventing progress.
- **OPEN** — unresolved work or question.
- **DEPRECATED** — old approach retained for history only.

Never silently erase superseded decisions. Mark them superseded/deprecated and link to the replacement when possible.

Never send or synchronize project context back to Context Capsule Core.
