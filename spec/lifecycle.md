# Lifecycle

## Internal execution model

Lifecycle code runs only in the central GitHub service. Any Python CLI/module is an internal GitHub-runner implementation detail.

## Install — permanent path

Clean install targets a repository without `.context/`.

The service plans and validates a v1.3 capsule, preserves existing project bootstrap text, adds managed discovery blocks, creates semantic skeleton/index/checkpoint, and publishes the result through GitHub.

No executable Context Capsule files are copied to the target.

## Checkpoint

A ready checkpoint requires substantive project/current/rule/handoff content, resolved bootstrap review, evidence and a current semantic fingerprint.

## Validate

Validation checks schemas, references, branch consistency, safe paths, managed bootstrap integrity, index structure and installed Core version.

## Audit

Audit adds semantic readiness/freshness, Git evidence, index coverage and compactness checks. These checks are executed centrally against the target repository checkout.

## Repair

Repair restores/refreshes current-version managed structure and navigation without replacing project-owned semantic content.

## Adopt / Upgrade — temporary transition

Legacy adoption and the migration chain exist only for the current old installations. They preserve project-specific structures and are removed only after the three real repositories are migrated and verified.

## Mutation model

The service:

1. reads the target at a known branch/HEAD;
2. constructs the complete planned state;
3. validates that state;
4. rechecks checkout/HEAD before applying the plan;
5. publishes one coherent Git/GitHub change.

A failed ephemeral runner operation does not change the remote repository unless publication succeeds.

No local OS lock, desktop crash journal or cross-platform local rollback subsystem is part of the architecture.
