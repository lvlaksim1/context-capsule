# Next actions

1. Finish adapting the existing lifecycle tests to v1.3 and add managed-bootstrap/readiness regressions.
2. Run CI on Linux and Windows/Python matrix; inspect logs and fix every failure.
3. Exercise clean install, legacy adopt, chained upgrade, repair, rollback/interruption and fresh-chat recovery end to end.
4. Test migrations against disposable copies of the three real legacy capsule shapes.
5. Update specifications/README from verified behavior, create a ready central checkpoint, then prepare the release/merge to `main`.
6. Keep legacy migration/adoption code until the three real repositories are migrated and verified; removal remains a later evidence-gated task.
7. Future recovery change: remove the hard `max_bytes` limit and any behavior that can block or omit needed history solely because of a byte budget. Mandatory project/current/rules/handoff/active-decision context must remain fully readable. Keep `.context/index.json` as a navigation/routing aid for deep history, not as an authorization/filter barrier that decides which history may be read. Control growth by compacting and summarizing durable context itself rather than truncating recovery.
