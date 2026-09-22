# Architecture

Context Capsule v2 represents a persistent Project Manager in the project repository itself.

## Permanent layers

- `project/`: objective identity, goals, architecture, constraints.
- `manager/`: stable manager identity, project-specific mandate, BDI-style active state, and Core-managed Manager Protocol.
- `memory/`: semantic, episodic, and procedural memory.
- `rules/` and `decisions/`: binding durable choices.
- `current/`: compact verified project state, blockers, next work.
- `handoffs/latest.md`: optional emergency/convenience summary rather than the continuity root.
- `dialogues/` and `history/`: deeper evidence/history.

`capsule.json` identifies the installed Core version and exact immutable `core_commit`. `manifest.json` maps project-owned context while preserving safe extensions.

## Runtime boundary

Chat/session history and workflow checkpoints are not Manager identity. The same manager may be instantiated by different runtimes over time.

## Mutation boundary

Canonical lifecycle mutations are planned and validated as a complete snapshot and published with an expected-parent non-forced Git ref update.

## Branch model

A permanent authoritative context branch may differ from a discovery branch. Disposable feature/runtime branches never become manager identity or durable context authority merely because execution occurs there.
