# Lifecycle

## Install

Use `install` for repositories without an existing capsule. It creates the v1.2 structure, technical metadata, navigation manifest, and compact project/current skeleton.

## Adopt

Use `adopt` when useful legacy `.context/` already exists but there is no Core `capsule.json`.

Adoption:
- preserves existing project-owned files;
- understands legacy manifest forms used by earlier Project Context Capsule installations;
- detects `authoritative_context_branch`, old authoritative maps, richer rules, and `.agent/` runtime separation;
- fills only missing standard semantic/current documents;
- writes Core metadata and a v1.2 navigation manifest.

## Validate

Checks required system files, metadata, manifest v2, project/current references, runtime and semantic-sync policy.

## Audit

Runs validation plus:
- compactness warnings for oversized current-state/handoff working-set files;
- Git lag warning when many commits have occurred since the last context/discovery update.

Audit warnings are prompts for semantic review, not proof that the capsule is stale.

## Repair

Restores missing standard files without overwriting project-owned content, then refreshes the manifest.

## Upgrade

Upgrades through the declared migration chain. v1.0 -> v1.1 -> v1.2 is supported without skipping explicit migration steps.

## CAS-aware mutation

`install`, `adopt`, `repair`, and `upgrade` accept `--expected-head`. When supplied, Core aborts if the checked-out repository HEAD differs, preventing blind overwrite after concurrent changes.
