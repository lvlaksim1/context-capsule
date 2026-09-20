# Next actions

1. Run the cleaned GitHub-only CI on the single pinned GitHub runner/Python version and fix all failures.
2. Exercise clean install, legacy adopt, chained upgrade, repair and readiness centrally against repository fixtures.
3. Verify the production-derived legacy shapes for `fgis-fsa-il`, `telegram-receiver` and `ai-agent-lab`.
4. Recompute/update the central ready checkpoint once the GitHub-only branch is verified.
5. Prepare merge/release to `main` only after those checks pass.
6. Keep legacy migration/adoption until the three real repositories are migrated and verified; remove it later as a separate change.
7. Future recovery change: remove the hard `max_bytes` limit and any behavior that can block or omit needed history solely because of a byte budget. Mandatory project/current/rules/handoff/active-decision context must remain fully readable. Keep `.context/index.json` only as navigation/routing for deep history. Control growth by compacting durable context itself rather than truncating recovery.
