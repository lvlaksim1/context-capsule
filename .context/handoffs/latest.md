# Latest handoff

## Completed

v1.3 hardening and the temporary known-legacy adapter are implemented on `work/core-v1.3`.

Current Core implementation commit: `822fb8500ae2c1b0192f4d0863a72678c877c928`.

The first real legacy migration exercised the `ai-agent-lab` adapter against its discovery/authority branch split. The migration preserved its existing semantic files, archived superseded bootstrap/protocol files, retained the special manager bootstrap and volatile `.agent/` authority, and survived subsequent target runtime commits.

No target repository context is copied into Core; only Core's own development state records that the adapter behavior was exercised.

## Verification boundary

Hosted GitHub Actions on the Core development branch are still not executing steps because no runner is assigned. Do not describe Core CI as green until the exact branch commit is actually executed.

## Next

Continue only with the two remaining known legacy migrations when requested, then remove unnecessary temporary compatibility before preparing a stable v1.3 release.
