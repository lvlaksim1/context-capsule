# Branch-aware context

A project may keep the authoritative capsule on a branch other than the repository default branch.

Manifest fields:
- `authoritative_branch` — full capsule and semantic authority;
- `discovery_branch` — first branch a fresh agent is expected to see;
- `branch_mode` — `single` or `redirect`.

For `redirect` mode, the discovery branch should contain minimal discovery shims that point to the authoritative context branch. Lifecycle mutation must be performed against the authoritative branch checkout.

Do not accidentally install a second independent capsule into the discovery branch.
