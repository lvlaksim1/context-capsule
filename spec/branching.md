# Branch-aware context

A project may keep the authoritative Context Capsule on a branch other than the repository default branch.

Manifest fields:

- `authoritative_branch` — branch containing the real capsule and semantic authority;
- `discovery_branch` — branch a fresh agent is expected to encounter first;
- `branch_mode` — `single` when they match, otherwise `redirect`.

## Mutation rule

The central GitHub service performs lifecycle mutation only against the authoritative branch and verifies the branch/HEAD before publication.

For redirect topology, the discovery branch must already exist. The service must not create a second independent capsule there.

## Discovery shims

The discovery branch may contain minimal `AGENTS.md`, `AI_CONTEXT.md` and/or `.context/ENTRYPOINT.md` instructions pointing to the authoritative branch. The authoritative branch contains the full semantic capsule.

Discovery text is project-owned unless it contains an explicit Context Capsule managed block.

## Read-only GitHub checks

Validation/audit may inspect a detached GitHub checkout. In that case branch-name evidence is incomplete, so the service must rely on explicit repository/ref metadata instead of pretending a local branch name proves authority.
