<!-- context-capsule:begin -->
# Context Capsule entrypoint

## Fast recovery

1. Read `.context/capsule.json` and `.context/manifest.json`.
2. Confirm the checked-out branch is the manifest's `authoritative_branch`.
3. Read project identity, goals, architecture and constraints.
4. Read all active project rules.
5. Read `current/state.md`, `current/blockers.md`, `current/next.md` and the latest handoff.
6. Read `.context/resume.json`. Treat `status=draft`, bootstrap-review entries, a fingerprint mismatch or newer implementation commits as a requirement to reconcile before continuing.
7. Use `.context/index.json` to select only task-relevant durable decisions/dialogues/history; do not bulk-load history by default.
8. Verify important stored claims against live code, CI/release evidence and any declared runtime authority.
9. If verified live facts are newer, live facts win. Record the resulting semantic change before substantial work continues.

If available, `python .context/tools/capsule_runtime.py check --ready` performs the repository-local readiness check and `python .context/tools/capsule_runtime.py resume --task "<task>"` emits a bounded recovery pack.

## Evidence priority

1. current explicit user instruction;
2. active confirmed requirement/decision;
3. verified current code, CI, release or runtime evidence;
4. current semantic state;
5. latest handoff;
6. active project rules;
7. historical decisions/dialogues;
8. older README/docs.

Do not silently resolve contradictions or erase superseded decisions. Use **FACT**, **DECISION**, **REQUIREMENT**, **RULE**, **PREFERENCE**, **HYPOTHESIS**, **BLOCKER**, **OPEN**, and **DEPRECATED** deliberately.

Keep `project/` durable and `current/` compact. Never synchronize project context back to Context Capsule Core.
<!-- context-capsule:end -->
