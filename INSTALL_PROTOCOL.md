# Installation protocol for agents

This document defines the canonical bootstrap procedure when a user asks to install Context Capsule into a repository.

## Inputs

- URL or `owner/name` of the target repository.
- Access sufficient to read and write that repository.
- This Context Capsule Core repository at an explicitly selected version/tag.

## Procedure

1. Read `VERSION`, `spec/architecture.md`, and `spec/lifecycle.md` from Context Capsule Core.
2. Inspect the target repository for `AI_CONTEXT.md` and `.context/capsule.json`.
3. If a capsule already exists, do not reinstall. Validate it and use upgrade/repair as appropriate.
4. Install the structure from `templates/` and generate `.context/capsule.json` pinned to the selected Core version.
5. Validate the installed structure.
6. Perform initial context capture **from the target repository only**:
   - project purpose;
   - durable rules and constraints;
   - important accepted decisions visible from repository evidence;
   - current state and active work;
   - latest handoff / next operation.
7. Write that captured context only into the target repository.
8. Re-read `.context/ENTRYPOINT.md` from the installed repository and verify clean recovery is possible.
9. Commit the capsule installation in the target repository.

## Prohibited behavior

- Do not copy target context into Context Capsule Core.
- Do not create a central registry of target repositories.
- Do not collect telemetry.
- Do not silently upgrade an installed capsule.
- Do not overwrite project-owned context during repair.
