# Current state

## FACT — Current semantic state

Context Capsule v1.3 hardening is implemented on `work/core-v1.3` from the clean v1.2 baseline. No code from the external-model checkpoint was used.

The current implementation provenance is `1018129caa6aae0677741c1da62504cf2ae3904e`.

All three known legacy capsule profiles have now been exercised against their real repositories:

- `ai-agent-lab` — redirect topology plus volatile `.agent/` runtime authority;
- `fgis-fsa-il` — rich single-branch semantic capsule with project/rules/decisions/dialogues;
- `telegram-receiver` — compact single-branch capsule expanded into the v1.3 stable project/current model from already verified repository context.

The migrations preserve target-owned semantic files, archive superseded system entrypoint/protocol where applicable, record exact Core provenance, and do not copy target project context into Core.

Hosted GitHub Actions for the Core development branch are still not executing steps because no runner is assigned; exact-commit hosted CI remains externally blocked and must not be described as green.
