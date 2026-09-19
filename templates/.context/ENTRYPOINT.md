# Context Capsule entrypoint

## Recovery protocol

1. Read `.context/capsule.json`.
2. Read `.context/manifest.json` and identify the authoritative context branch and discovery branch.
3. Read project identity, goals, architecture, and constraints referenced by the manifest.
4. Read active project rules.
5. Read current state, blockers, and next actions.
6. Read the latest handoff.
7. Read relevant durable decisions.
8. Read dialogue evidence only when chronology or reasoning matters.
9. Read deeper history only when needed.
10. Reconcile the recovered context with the live authoritative repository branch, current CI/workflows, and any declared runtime authority.
11. If verified live facts are newer than stored context, live facts win; classify the semantic change and update the capsule before substantial work continues.

## Evidence priority

1. current explicit user instruction;
2. active confirmed requirement/decision;
3. verified current code, CI, release, or runtime evidence;
4. `.context/current/*`;
5. latest handoff;
6. active rules;
7. historical decisions/dialogues;
8. older README/docs.

Do not silently reconcile contradictions. Record the conflict and request a decision only when work cannot safely continue.

## Context semantics

Use: **FACT**, **DECISION**, **REQUIREMENT**, **RULE**, **PREFERENCE**, **HYPOTHESIS**, **BLOCKER**, **OPEN**, **DEPRECATED**.

Never silently erase superseded decisions. Mark them superseded/deprecated and link to the replacement.

Keep the current working set compact. Move resolved or superseded material into decisions, dialogues, or history rather than accumulating it in `current/` or `handoffs/latest.md`.

Never synchronize project context back to Context Capsule Core.
