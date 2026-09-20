# Current state

## FACT — Current semantic state

Context Capsule v1.3 hardening is implemented on `work/core-v1.3` from the clean v1.2 baseline. No code from the external-model checkpoint was used.

Implemented capabilities include atomic one-commit GitHub publication from an expected parent, repository-path confinement, preservation of project-owned manifest extensions and rich legacy category structure, managed bootstrap blocks, exact Core provenance, VALID vs READY separation, deterministic bounded fresh-chat recovery with active-state priority, and temporary repository-gated adapters for the three known legacy capsules.

The current implementation provenance is `822fb8500ae2c1b0192f4d0863a72678c877c928`.

The temporary `ai-agent-lab` adapter has been exercised against its real two-branch topology. The target's rich project context and manager/live-runtime integration were preserved, and subsequent target runtime commits retained the migrated v1.3 capsule. No target project context is stored in Core.

Hosted GitHub Actions for this Core development branch still terminate without an assigned runner (`runner_id=0`, `steps=[]`), so exact-commit hosted CI remains externally blocked and must not be described as green.
