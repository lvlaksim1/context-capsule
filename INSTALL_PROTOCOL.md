# Context Capsule GitHub installation protocol

## Product boundary

The user does not install or run anything locally.

All Context Capsule operations are initiated and executed inside GitHub by the central service. Internal scripts may run in an ephemeral GitHub-hosted checkout, but this is not a user-facing runtime.

## Permanent path: clean installation

For a repository without an existing capsule, the GitHub service:

1. reads the target repository and authoritative branch;
2. verifies the expected HEAD when available;
3. refuses an existing `.context/` unless the operation is an explicit legacy adoption;
4. creates the standard context structure;
5. preserves pre-existing project instructions in shared bootstrap files;
6. adds only the Context Capsule managed bootstrap block;
7. creates `manifest.json`, `index.json` and a draft `resume.json`;
8. validates the planned state before publication;
9. commits/publishes the coherent change through GitHub.

The target repository receives data/instructions only, never Context Capsule executables.

## Context capture and readiness

After clean installation, repository-specific semantics must be populated from verified GitHub evidence. `CAPSULE_TODO` templates are not considered continuation-ready.

The central service marks a checkpoint ready only after required semantic content, evidence, bootstrap review and freshness checks pass.

## Branch topology

The lifecycle operation runs against the authoritative context branch. The service must verify branch identity and must not create a second independent capsule in a discovery branch.

For split topology, the discovery branch contains only the minimal pointer needed to locate the authoritative branch.

## Mutation safety

The service builds a complete plan against a known branch/HEAD. Before publication it verifies that the checkout still corresponds to that state.

Remote publication must use Git/GitHub concurrency protection so a stale service run cannot overwrite a newer repository state.

No local desktop lock, crash journal, Windows path compatibility layer or local rollback service is required.

## Existing legacy capsule — temporary only

Until the three known old installations are migrated, legacy adoption/migration preserves:

- custom manifest fields;
- richer project/current paths;
- declared decisions/dialogues/history outside standard folders;
- project-specific rule files;
- custom bootstrap text;
- split authoritative/discovery branches;
- separate live runtime authorities such as `.agent/`.

Unknown project bootstrap text is preserved and requires explicit review before readiness.

After `fgis-fsa-il`, `telegram-receiver` and `ai-agent-lab` are migrated and verified, the legacy transition layer may be removed in a separate change.

## Prohibited

- requiring the user to run Python or any Context Capsule executable locally;
- installing `.context/tools/**` into target repositories;
- maintaining a central copy of target-project context;
- telemetry/installation statistics;
- silent replacement of unknown project instructions;
- treating structural validity as semantic readiness.
