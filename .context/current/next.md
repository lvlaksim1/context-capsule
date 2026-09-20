# Next actions

1. Keep `main` and all real target repositories unchanged until the user requests the next stage.
2. When GitHub Actions actually assigns a runner again, run the v1.3 unit suite plus central `validate`, `ready`, and `recover` gates.
3. The next production stage is real migration/verification in order: `fgis-fsa-il`, `telegram-receiver`, then `ai-agent-lab`.
4. After those three migrations, remove or isolate temporary legacy compatibility before a stable v1.3 release.
