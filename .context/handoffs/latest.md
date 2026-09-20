# Latest handoff — GitHub-only v1.3 cleanup checkpoint

## User correction

Context Capsule is exclusively a GitHub service. Nothing is installed or executed on the user's computer.

## Corrected architecture

- Central executable implementation: `lvlaksim1/context-capsule`.
- Execution environment: GitHub automation / ephemeral GitHub-hosted checkout.
- Target repositories: context data + discovery/bootstrap text only.
- No target-installed `.context/tools/**`.
- No local Python requirement.
- No Windows/Linux desktop compatibility matrix.
- No OS-level local lock/crash journal subsystem.

## Removed from the v1.3 branch

- copied runtime/schema bundle in target repositories;
- tests enforcing copied runtime parity;
- Windows CI matrix and multi-Python compatibility matrix;
- desktop OS locking, journal, atomic-file rollback and Windows path work;
- bootstrap/docs instructions telling a target repository to execute local Capsule Python.

## Retained

- v3 schemas and strict central validation;
- managed bootstrap blocks preserving unknown project instructions;
- branch/HEAD/dirty-context checks;
- repository path/symlink confinement;
- semantic index and draft/ready checkpoint;
- central readiness/recovery logic;
- production-derived legacy migration fixtures;
- temporary migration chain through v1.3.

## Next exact step

Run GitHub-only CI after cleanup, fix all failures, then verify migration fixtures and central self-audit. Do not merge PR #1 before the cleaned branch is green.

## Future recorded change

Remove the hard recovery-pack byte budget. `index.json` remains navigation only; it must never prevent access to needed context.
