# Current blockers and open risks

## RELEASE BLOCKERS

None.

## CLOSED — GitHub-hosted runner availability

The earlier hosted-runner failure for the private repository is resolved after making `context-capsule` public.

A rerun of the same stable `main` workflow received a GitHub-hosted `ubuntu-latest` runner and completed every CI step successfully.

No product or CI blocker remains for v1.3.

## CLOSED — v1.3.0 provenance ambiguity

The patch release v1.3.1 establishes a single canonical Core commit and removes the previous situation where different implementations carried the same v1.3.0 label.
