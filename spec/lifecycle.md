# Lifecycle

## 1. Install

Installation is performed against a target repository.

The installer:

1. detects whether a capsule is already installed;
2. refuses destructive reinstallation;
3. creates the standard directory structure;
4. writes system-owned bootstrap files;
5. creates empty project-owned context documents only when missing;
6. records the pinned Core version in `.context/capsule.json`;
7. validates structural integrity.

After structural installation, an agent performs **initial context capture** from the target repository itself. That capture is written only to the target repository.

## 2. Normal operation

Agents begin with `AI_CONTEXT.md`, then follow `.context/ENTRYPOINT.md`.

Routine project work reads and updates the target repository capsule only. Context Capsule Core is not contacted.

## 3. Validate

Validation checks structure, metadata, required files, version consistency, and basic invariants. It does not upload project content.

## 4. Upgrade

Upgrade is explicit. The installed version is compared with the requested Core version. A declared migration must exist for version changes that modify structure or semantics.

Project-owned context is preserved.

## 5. Repair

Repair restores missing system-owned files and structural invariants. It MUST NOT overwrite project-owned context.

## 6. Removal

Removal is intentionally not automated in v1.0.0 because `.context/` contains project history. Any future removal command must require an explicit archival policy.
