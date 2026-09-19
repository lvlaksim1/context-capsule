# Architecture

## Purpose

Context Capsule provides durable, repository-local context for human/AI project work. A new agent should be able to recover project identity, constraints, decisions, current state, and the latest handoff from the repository itself.

## Architectural invariants

1. **Repository-local context.** The complete context of a target project is stored inside that target repository.
2. **No reverse synchronization.** Context Capsule Core MUST NOT store, aggregate, mirror, index, or receive project context from target repositories.
3. **Autonomous installed instance.** A target repository continues to use its installed capsule even when Context Capsule Core is unavailable.
4. **Pinned version.** Each installed capsule records the exact capsule version in `.context/capsule.json`.
5. **Explicit upgrades.** New Core versions do not silently change installed repositories. Upgrades require an explicit migration.
6. **Ownership separation.** System-owned capsule files and project-owned context files have different lifecycle rules.
7. **History preservation.** Upgrade and repair operations MUST NOT erase project decisions, history, rules, or handoffs.
8. **No bootstrap ZIP dependency.** The canonical bootstrap source is this repository, not an out-of-band archive.

## Two layers

### Core layer

Lives in this repository and contains:

- installer and validator;
- canonical templates;
- schema definitions;
- lifecycle and precedence rules;
- migrations;
- conformance tests.

### Installed project layer

Lives in each target repository and contains:

- `AI_CONTEXT.md` — discovery pointer;
- `.context/ENTRYPOINT.md` — deterministic recovery entrypoint;
- `.context/capsule.json` — installed schema/version metadata;
- `.context/current/` — current project state;
- `.context/rules/` — active project rules;
- `.context/decisions/` — durable decisions;
- `.context/handoffs/latest.md` — current session handoff;
- `.context/history/` — compact historical records.

## Ownership model

System-owned files may be installed or repaired from Core:

- `AI_CONTEXT.md`
- `.context/ENTRYPOINT.md`
- `.context/capsule.json` structure

Project-owned files are never replaced by generic Core content after initial creation:

- `.context/current/**`
- `.context/rules/**`
- `.context/decisions/**`
- `.context/handoffs/**`
- `.context/history/**`
