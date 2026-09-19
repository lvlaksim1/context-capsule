# Current state

## FACT

Released baseline remains Core v1.2.0 on `main` at `2965c17`. Development is isolated on `work/seamless-context-v1.3`; draft PR #1 is open and must not be merged yet.

The v1.3 implementation is now integrated rather than merely drafted: lifecycle mutations are transaction-planned and journaled, repository paths/symlinks are confined, checkout/dirty-context preconditions are enforced, schema v3 is executable, managed bootstrap blocks preserve pre-existing project instructions, and each installed repository receives local validation/recovery tooling plus `index.json` and `resume.json`.

The central repository itself has been migrated structurally to the v1.3 format. Final correctness is not yet claimed because the complete cross-platform test matrix and production-copy migration tests are still pending.
