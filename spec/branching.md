# Branch-aware context

A project may keep its authoritative Context Capsule on a branch other than the repository default branch.

Manifest fields:

- `authoritative_branch` — branch containing the real capsule and semantic authority;
- `discovery_branch` — branch a fresh agent is expected to encounter first;
- `branch_mode` — `single` when they match, otherwise `redirect`.

## Mutation rule

All lifecycle writes must run from the checked-out authoritative branch. `--branch` verifies that condition; it never switches branches.

For redirect topology, the discovery branch must already exist. Core must not accidentally install a second independent capsule there.

## Discovery shims

The discovery branch may contain minimal `AGENTS.md`, `AI_CONTEXT.md` and/or `.context/ENTRYPOINT.md` instructions pointing to the authoritative branch. The authoritative branch contains the full semantic capsule.

Discovery text is project-owned unless it contains an explicit Context Capsule managed block.

## Detached checkouts

Read-only validation/audit can run in a detached CI checkout. In that case branch authority cannot be proven from `git branch --show-current`, so runtime inspection reports that limitation instead of performing mutation.

Mutating lifecycle commands require a named branch.
