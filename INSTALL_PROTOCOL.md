# Canonical GitHub installation protocol

## Clean installation

1. Read the target branch HEAD and tree.
2. Read existing `AI_CONTEXT.md` / `AGENTS.md` if present and confirm there is no existing `.context/`.
3. Capture the target project's durable semantic context.
4. Build the complete desired snapshot in memory using the pinned Core commit SHA.
5. Run structural validation and recovery-readiness checks against that planned snapshot.
6. Create one Git tree based on the original tree.
7. Create one commit whose parent is the original expected HEAD.
8. Re-read the branch HEAD. If it changed, stop without moving the branch.
9. Update the branch ref non-forced. A concurrent advance must therefore reject publication.

The only branch-visible mutation is the final ref update. A failed publication may leave unreachable Git objects, but it does not partially install the capsule on the target branch.

## Shared bootstrap files

Context Capsule owns only text between:

`<!-- context-capsule:begin -->`

and

`<!-- context-capsule:end -->`

Existing project instructions outside that block are preserved.

## Legacy transition

Temporary adoption is allowed only for:

- `lvlaksim1/fgis-fsa-il`
- `lvlaksim1/telegram-receiver`
- `lvlaksim1/ai-agent-lab`

Actual production migration of those repositories is a later stage and is not part of the clean-install foundation.
