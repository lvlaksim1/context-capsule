# Current state

## FACT — Current semantic state

Context Capsule v1.3 permanent product surface has been simplified after completing all three known legacy migrations.

Implementation commit: `f7b947b0974bc697cf61f553d7f48294413d39d5`.

The temporary repository-specific migration layer is retired:

- `installer/legacy.py` is removed;
- the public/local `adopt` command is removed;
- repository-specific legacy tests are removed;
- the migration registry no longer lists temporary legacy profiles;
- product documentation now treats legacy migration as completed history, not a supported normal lifecycle path.

The permanent v1.3 surface remains clean install, non-destructive repair, structural VALID, semantic READY, deterministic bounded fresh-chat recovery, managed bootstrap blocks, repository path confinement, exact Core provenance, and atomic one-commit GitHub publication.

All three previously known legacy repositories are already on v1.3 and do not depend on the removed adapter at runtime.

Hosted GitHub Actions still does not execute any job step on this development branch: the cleanup run ended with `runner_id=0` and `steps=[]`. Therefore exact-commit hosted CI is still pending and must not be described as green.
