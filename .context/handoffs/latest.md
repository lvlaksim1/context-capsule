# Latest handoff

## v2 Project Manager development state

Context Capsule v1.3.1 remains the stable production line on `main`. No consumer repository has been migrated to v2.

The v2 Project Manager development line lives on `v2-manager-runtime`.

Authority coordinates:

- manager-state authority: `v2-manager-runtime`;
- product authority: `main`;
- `authoritative_branch` is only a compatibility alias of manager-state authority;
- discovery is a separate bootstrap coordinate.

Evidence semantics are explicit: `confirm`, `supersede`, `conflict`; freshness alone never implies supersession.

Fresh-runtime recovery has successfully demonstrated identity continuity, authority separation, live reconciliation, and correct handling of newer confirming CI evidence.

Current development Core source: `6b8477d382bbf5cd8d13bd914b2374473560a43d`.
Supporting verification evidence includes GitHub Actions run `35774586971` — success. This is an evidence pointer, not a requirement to track the latest confirming run.

Next work follows owner direction and verified project evidence. Do not publish stable v2 or migrate consumers without explicit owner approval.
