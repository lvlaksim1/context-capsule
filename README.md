# Context Capsule Core

Context Capsule is a GitHub-only service for durable project context across independent chats/agents.

The central repository `lvlaksim1/context-capsule` contains all executable logic. Target repositories contain only their own context data and lightweight discovery instructions. Nothing from Context Capsule is installed or executed on the user's computer.

## v1.3 target-repository model

A target repository may contain:

- `.context/capsule.json` — installed Core version and managed bootstrap hashes;
- `.context/manifest.json` — branch topology and navigation to project context;
- `.context/project/` — stable identity, goals, architecture and constraints;
- `.context/current/` — compact current state, blockers and next actions;
- `.context/decisions/`, `.context/dialogues/`, `.context/history/` — durable semantic evidence;
- `.context/index.json` — navigation metadata for durable history;
- `.context/resume.json` — evidence-backed continuation checkpoint;
- `AGENTS.md`, `AI_CONTEXT.md`, `.context/ENTRYPOINT.md`, `.context/protocol.md` — discovery/bootstrap text.

There is no installed Python runtime, bundled schema copy, local daemon or desktop component in a target repository.

## Execution boundary

Installation, validation, migration, repair, indexing, readiness checks and future maintenance are executed by GitHub automation from the central Core repository.

The internal Python modules are implementation details of the GitHub service. They run on the GitHub runner, not on the user's machine.

## Valid vs ready

A capsule can be structurally valid but not yet ready for seamless continuation.

- **valid** — metadata, references and managed bootstrap are structurally consistent;
- **ready** — repository-specific semantics have been captured, reconciled with current GitHub evidence, indexed and checkpointed.

Fresh clean installation intentionally starts valid-but-draft until project-specific context is populated.

## Safety

The GitHub service:

- plans the target state before modifying the workflow checkout;
- confines managed paths to the repository;
- rejects symlink/path traversal;
- verifies authoritative branch and optional expected HEAD;
- refuses stale/dirty context writes;
- preserves unknown project-owned bootstrap text;
- publishes changes through normal Git/GitHub concurrency controls.

The remote Git repository is the transaction boundary; no desktop OS lock or local crash journal is part of the product.

## Temporary legacy support

`adopt` and chained legacy migrations are temporary mechanisms retained only until the existing old capsules in:

- `lvlaksim1/fgis-fsa-il`;
- `lvlaksim1/telegram-receiver`;
- `lvlaksim1/ai-agent-lab`

are migrated and verified.

They are not part of the permanent clean-install architecture.

See `INSTALL_PROTOCOL.md` and `spec/`.
