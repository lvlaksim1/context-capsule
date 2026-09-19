# Current state

## Project purpose

`context-capsule` is the canonical Core repository for the Context Capsule standard, installer, validator, lifecycle rules, templates, schemas, and migrations.

## Architecture

The complete context of every target repository remains inside that target repository. Context Capsule Core never stores, aggregates, mirrors, indexes, or receives target repository context.

Installed capsules are autonomous and version-pinned. Core is consulted only for install, validate, explicit upgrade, or repair.

## Current status

Core v1.0.0 bootstrap implementation is prepared and passes its initial tests. The canonical private repository `lvlaksim1/context-capsule` has been created through `lvlaksim1/repo-factory`.

## Active work

Publish this v1.0.0 bootstrap to `lvlaksim1/context-capsule`, then verify clean installation into a separate test repository.

## Known blockers

None. Repository creation is delegated to `lvlaksim1/repo-factory`.
