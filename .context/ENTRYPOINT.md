<!-- context-capsule:begin -->
# Context Capsule entrypoint

## Recovery

1. Read `.context/capsule.json` and `.context/manifest.json`.
2. Follow the manifest to the authoritative context branch.
3. Read project identity, goals, architecture and constraints.
4. Read all active project rules.
5. Read `current/state.md`, `current/blockers.md`, `current/next.md` and the latest handoff.
6. Read `.context/resume.json`. Treat `status=draft`, unresolved bootstrap review, a semantic fingerprint mismatch, or newer implementation evidence as requiring reconciliation.
7. Use `.context/index.json` as navigation for decisions/dialogues/history. It is not a filter that may hide needed context.
8. Verify important stored claims against current GitHub repository, CI/release evidence and any declared runtime authority.
9. If verified live facts are newer, live facts win; persist the semantic consequence back into the capsule.

Validation, migration, repair and readiness checks are performed by the central Context Capsule GitHub service. Nothing from Context Capsule needs to be executed on the user's computer.

## Evidence priority

1. current explicit user instruction;
2. active confirmed requirement/decision;
3. verified current code, CI, release or runtime evidence;
4. current semantic state;
5. latest handoff;
6. active project rules;
7. historical decisions/dialogues;
8. older README/docs.

Do not silently resolve contradictions or erase superseded decisions. Keep `project/` durable and `current/` compact. Never synchronize target-project context into the central Core repository.
<!-- context-capsule:end -->
