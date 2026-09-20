# Canonical GitHub lifecycle protocol

## Clean installation

1. Read the target branch HEAD and tree.
2. Read existing `AI_CONTEXT.md` / `AGENTS.md` if present and confirm there is no existing `.context/`.
3. Capture the target project's durable semantic context.
4. Build the complete desired snapshot in memory using the pinned Core commit SHA.
5. Run structural validation and recovery-readiness checks against that planned snapshot.
6. Create one Git tree based on the original tree.
7. Create one commit whose parent is the original expected HEAD.
8. Re-read the branch HEAD. If it changed, stop without moving the branch.
9. Update the branch ref non-forced.

The only branch-visible mutation is the final ref update. A failed publication may leave unreachable Git objects, but it does not partially install the capsule on the target branch.

## Repair / Core refresh

For an installed v1.3 capsule, repair/refresh must:

- preserve project-owned semantic files and unknown safe manifest extensions;
- update only Core-managed bootstrap/metadata/index structure;
- use the same expected-parent, one-commit publication model;
- never reinterpret an unknown historical capsule format as a supported legacy migration.

## Shared bootstrap files

Context Capsule owns only text between:

`<!-- context-capsule:begin -->`

and

`<!-- context-capsule:end -->`

Existing project instructions outside that block are preserved.

## Legacy policy

The one-time migration bridge for `fgis-fsa-il`, `telegram-receiver`, and `ai-agent-lab` completed on 2026-09-20 and has been removed from the permanent Core.

Future unknown legacy layouts are not automatically adopted. A deliberate one-off migration must first be designed from the repository's actual evidence rather than expanding the permanent compatibility surface.

## Permanent authoritative context branch

For repositories that routinely use temporary feature branches, prefer a permanent authoritative context branch.

1. Create or update the permanent context branch first and make its manifest authoritative_branch=<context branch>, discovery_branch=<default branch>, branch_mode=redirect.
2. Validate and READY-check the authoritative snapshot before exposing the redirect.
3. Convert the default branch to discovery-only bootstrap: managed AI_CONTEXT.md, managed AGENTS.md, and .context/ENTRYPOINT.md redirect only. A discovery branch must not retain .context/capsule.json, .context/manifest.json, or semantic working-set files that can be mistaken for current authority.
4. Publish the authoritative branch first, then the discovery branch. Each branch update uses its own expected-parent atomic commit and non-forced ref update.
5. Feature branches never become Context Capsule authority. Their names, PRs, tests, and work state are recorded as semantic facts in the permanent context branch.
6. After merge or release, update the same permanent context branch; no authority handoff back to main is required.
