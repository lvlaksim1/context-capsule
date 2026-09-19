# Current state

## Project purpose

`context-capsule` is the canonical Core repository for the Context Capsule standard, installer/adopter, validator, lifecycle rules, templates, schemas, and migrations.

## Architecture

The complete context of every target repository remains inside that target repository. Core never stores, aggregates, mirrors, indexes, or receives target repository context.

`capsule.json` is the technical installation/version passport. `manifest.json` is the navigation index for the actual project context and authoritative branch.

## Current status

Core v1.1.0 is published on `main`. It includes manifest navigation, typed context semantics, `AGENTS.md`, protocol/dialogue layers, live-state reconciliation, safe legacy `adopt`, and an executable v1.0.0 -> v1.1.0 migration.

## Verification

The v1.1.0 GitHub Actions test job completed successfully. Five lifecycle tests pass: install, reinstall refusal, legacy adoption, repair preservation, and v1.0 -> v1.1 upgrade. Central self-validation also passes.

## Active work

Use `lvlaksim1/telegram-receiver` as the first production legacy-adoption test when requested.

## Known blockers

None.
