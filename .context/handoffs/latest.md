# Latest handoff

## v2 Project Manager behavioral continuity verified through PM-003

Context Capsule v1.3.1 remains the stable production line on `main`. No consumer repository has been migrated to v2.

The v2 Project Manager development line lives on `v2-manager-runtime`.

Authority coordinates:

- manager-state authority: `v2-manager-runtime`;
- product authority: `main`;
- `authoritative_branch` is only a compatibility alias of manager-state authority;
- discovery is a separate bootstrap coordinate.

Evidence semantics are explicit: `confirm`, `supersede`, `conflict`; freshness alone never implies supersession.

Behavioral acceptance now has a durable suite in `spec/v2-acceptance.md`:

- PM-001 Cold reinstantiation — PASS;
- PM-002 Authority separation — PASS;
- PM-003 Evidence revision/freshness — PASS;
- PM-004 Origin-bound memory authority — next.

The latest fresh-runtime acceptance correctly treated the newest successful CI as confirming evidence and treated only the already-completed acceptance task as semantic supersession. This validates the fix for the CI/write-back loop.

Current development Core source: `13ef0996789ded21d33fe30af9906898816240e2`.
Verification evidence: GitHub Actions run `35777082840` — success.

Research for PM-004 indicates that persistent-memory attacks can launder low-trust origin through agent summarization, trusted-tool echoes, or manufactured corroboration. PM-004 therefore tests authority non-amplification, not merely the presence of textual `source:` / `authority:` labels.

Do not publish stable v2 or migrate consumers without explicit owner approval.
