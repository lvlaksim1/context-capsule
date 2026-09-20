# Next actions

1. Stop adding new legacy compatibility cases.
2. Isolate or remove temporary legacy migration logic now that `ai-agent-lab`, `fgis-fsa-il`, and `telegram-receiver` are migrated.
3. Re-run the exact Core unit/VALID/READY/recover gates when GitHub Actions assigns a runner normally.
4. After exact verification, simplify the permanent product around clean install, managed upgrades, READY recovery, and atomic GitHub publication.
5. Prepare a stable v1.3 release only after the temporary migration layer is no longer part of the normal path.
