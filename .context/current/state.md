# Current state

## Project purpose

`context-capsule` is the canonical Core repository for the Context Capsule standard, installer, validator, lifecycle rules, templates, schemas, and migrations.

## Architecture

The complete context of every target repository remains inside that target repository. Context Capsule Core never stores, aggregates, mirrors, indexes, or receives target repository context.

Installed capsules are autonomous and version-pinned. Core is consulted only for install, validate, explicit upgrade, or repair.

## Current status

Core v1.0.0 is published in the canonical private repository `lvlaksim1/context-capsule`. Initial local tests and self-validation pass.

## Active work

Verify the published GitHub CI run, then perform a clean installation/bootstrap test against a separate repository.

## Known blockers

None. Repository creation is delegated to `lvlaksim1/repo-factory`.
