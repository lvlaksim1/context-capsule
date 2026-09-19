# Context Capsule entrypoint

Read in this order:

1. `.context/capsule.json`
2. `.context/rules/project-rules.md`
3. `.context/current/state.md`
4. `.context/decisions/`
5. `.context/handoffs/latest.md`
6. `.context/history/` only when deeper history is required

Then verify the recovered state against the repository at the current commit.

If repository facts are newer than the capsule, treat repository facts as authoritative and update the capsule before continuing substantial work.

Never send or synchronize project context back to Context Capsule Core.
