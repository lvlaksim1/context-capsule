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
