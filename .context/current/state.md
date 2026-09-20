# Current state

## FACT — Current semantic state

Context Capsule v1.3 hardening items 1–9 are implemented on `work/core-v1.3` from the clean v1.2 baseline. No code from the external-model checkpoint was used.

Implemented capabilities: one-commit GitHub publication from an expected parent, repository-path confinement, preservation of manifest extensions/custom indexed paths, managed bootstrap blocks, exact `core_commit` provenance, separate VALID and READY checks, deterministic fresh-chat recovery, focused negative tests, and temporary repository-gated adapters for the three known legacy capsules.

The exact Core implementation provenance for this development capsule is `15635af84b5d3f75062174de26e490f9f24bb521`.

Verification status is deliberately split: the development prototype passed 17 focused local tests, while the exact published branch commit has not been executed by GitHub Actions because the service has not assigned a runner to any run on this branch. The branch therefore remains development-only and is not a released v1.3.
