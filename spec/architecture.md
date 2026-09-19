# Architecture

## Purpose

Context Capsule provides durable, repository-local context for human/AI project work. A fresh agent should recover project identity, constraints, accepted decisions, current state, evidence, and the latest handoff from the repository itself.

## Architectural invariants

1. **Repository-local context.** The complete context of a target project is stored inside that target repository.
2. **No reverse synchronization.** Context Capsule Core MUST NOT store, aggregate, mirror, index, or receive project context from target repositories.
3. **Autonomous installed instance.** A target repository continues to use its installed capsule even when Core is unavailable.
4. **Pinned version.** Each installed capsule records its exact Core version in `.context/capsule.json`.
5. **Explicit upgrades.** New Core versions do not silently change installed repositories.
6. **Ownership separation.** System-owned capsule files and project-owned context have different lifecycle rules.
7. **History preservation.** Upgrade, repair, and legacy adoption MUST NOT erase project decisions, dialogue evidence, history, rules, or handoffs.
8. **Repository bootstrap.** The canonical bootstrap source is this repository, not an out-of-band ZIP archive.
9. **Manifest navigation.** `.context/manifest.json` maps actual project-owned context paths; project content is not forced into one global filename convention.
10. **Live-state verification.** Capsule recovery is incomplete until the agent reconciles stored context with the authoritative branch and relevant current repository/CI/runtime evidence.

## Core layer

Lives in this repository and contains installer/adopter/validator/repair/upgrade tooling, canonical templates, schemas, lifecycle rules, migrations, and conformance tests.

## Installed project layer

A standard installation contains:

- `AI_CONTEXT.md` — discovery pointer;
- `AGENTS.md` — secondary agent discovery pointer;
- `.context/ENTRYPOINT.md` — deterministic recovery protocol;
- `.context/capsule.json` — technical installation/version passport;
- `.context/manifest.json` — navigation index and authoritative branch;
- `.context/protocol.md` — semantic/update rules;
- `.context/current/` — current state;
- `.context/rules/` — active rules;
- `.context/decisions/` — durable decisions and supersession chain;
- `.context/handoffs/latest.md` — current handoff;
- `.context/dialogues/` — compact evidence-rich investigation records;
- `.context/history/` — other compact historical context.

## Two metadata files, two jobs

`capsule.json` answers: **what Context Capsule installation is this?**

`manifest.json` answers: **where is this project's context and which branch is authoritative?**

Keeping these roles separate lets Core evolve technically without forcing project-owned context into a rigid filename layout.

## Legacy adoption

`adopt` is the transition path for repositories that already contain a useful `.context/` created by older mechanisms. Adoption preserves existing context files and enriches them with Core metadata/navigation rather than reinstalling or renaming them.
