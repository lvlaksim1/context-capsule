# Installation and adoption protocol for agents

## New repository

1. Select an explicit stable Context Capsule Core version.
2. Inspect the target for `AI_CONTEXT.md`, `AGENTS.md`, `.context/`, and `.context/capsule.json`.
3. If no capsule exists, run `install` with the target repository and authoritative branch.
4. Perform initial context capture from the target repository only.
5. Refresh/validate `.context/manifest.json`.
6. Re-read `.context/ENTRYPOINT.md` and verify recovery against the live authoritative branch.
7. Commit the installation in the target repository.

## Existing legacy capsule

If `.context/` exists but `.context/capsule.json` does not, do **not** reinstall. Run `adopt`.

Adoption must preserve existing project context, including project-specific filenames and richer old structures. It may add missing system files and enrich the navigation manifest, but it must not rename or overwrite project-owned context merely to satisfy a template.

## Prohibited behavior

- Do not copy target context into Context Capsule Core.
- Do not create a central registry or telemetry store.
- Do not silently upgrade versions.
- Do not destroy superseded decisions or dialogue evidence.
- Do not assume the handoff is current without checking the authoritative branch and relevant live evidence.
