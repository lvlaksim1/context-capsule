# Current state

## Project purpose

`context-capsule` is the canonical Core repository for the Context Capsule standard, installer/adopter, validator, lifecycle rules, templates, schemas, and migrations.

## Architecture

The complete context of every target repository remains inside that target repository. Core never stores, aggregates, mirrors, indexes, or receives target repository context.

`capsule.json` is the technical installation/version passport. `manifest.json` is the navigation index for the actual project context and authoritative branch.

## Current status

Core v1.1.0 has been implemented locally on top of v1.0.0. It adds manifest navigation, typed context semantics, `AGENTS.md`, protocol/dialogue layers, live-state reconciliation, safe legacy `adopt`, and an executable v1.0.0 -> v1.1.0 migration.

## Verification

Five lifecycle tests pass: install, reinstall refusal, legacy adoption, repair preservation, and v1.0 -> v1.1 upgrade. Self-validation passes after upgrading this repository's own capsule.

## Active work

Publish v1.1.0 to `lvlaksim1/context-capsule` and verify GitHub CI. Then use `lvlaksim1/telegram-receiver` as the first production legacy-adoption test.

## Known blockers

None.
