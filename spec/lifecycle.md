# Lifecycle

## 1. Install

Use `install` only for a repository that does not already contain a capsule. It creates the standard structure, writes `capsule.json` and `manifest.json`, pins the Core version, and validates references.

After structural installation, initial context capture is performed from the target repository and written only to that repository.

## 2. Adopt legacy capsule

Use `adopt` when `.context/` already exists but `.context/capsule.json` does not.

Adoption:

1. refuses to overwrite existing project-owned files;
2. preserves an existing legacy `manifest.json` and its custom fields;
3. creates the technical `capsule.json` passport;
4. enriches `manifest.json` with the v1 navigation contract;
5. adds missing discovery/protocol files only when absent;
6. indexes existing rules, decisions, dialogues, history, handoff, and current state;
7. validates all indexed paths.

## 3. Normal operation

Agents begin with `AI_CONTEXT.md` or `AGENTS.md`, follow `ENTRYPOINT.md`, then use `manifest.json` for actual paths. Routine work does not contact Core.

## 4. Validate

Validation checks technical metadata, authoritative branch metadata, system discovery files, manifest integrity, and every indexed path. It never uploads project content.

## 5. Repair

Repair restores missing system-owned files and refreshes the navigation manifest. It does not overwrite project-owned context.

## 6. Upgrade

Upgrade is explicit and migration-driven. v1.0.0 -> v1.1.0 adds the manifest/protocol/agent-discovery/dialogue layer without replacing existing project context.

## 7. Handoff/update discipline

Before a work session ends, update current state and `handoffs/latest.md`; refresh the manifest when project-context files were added/moved. Preserve superseded decisions rather than rewriting history.

## 8. Removal

Removal remains intentionally non-automated because `.context/` contains project history and decisions.
