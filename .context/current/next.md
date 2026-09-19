# Next actions

1. Finish adapting the existing lifecycle tests to v1.3 and add managed-bootstrap/readiness regressions.
2. Run CI on Linux and Windows/Python matrix; inspect logs and fix every failure.
3. Exercise clean install, legacy adopt, chained upgrade, repair, rollback/interruption and fresh-chat recovery end to end.
4. Test migrations against disposable copies of the three real legacy capsule shapes.
5. Update specifications/README from verified behavior, create a ready central checkpoint, then prepare the release/merge to `main`.
6. Keep legacy migration/adoption code until the three real repositories are migrated and verified; removal remains a later evidence-gated task.
