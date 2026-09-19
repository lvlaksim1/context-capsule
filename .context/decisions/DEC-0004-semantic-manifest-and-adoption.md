# DEC-0004 — Semantic manifest and legacy adoption

- Status: active
- Date: 2026-09-20

## Decision

Context Capsule Core v1.1.0 separates the technical installation passport (`capsule.json`) from the project navigation index (`manifest.json`).

The manifest records the authoritative branch and actual paths to project-owned rules, current state, handoff, decisions, dialogue evidence, and history. Project-owned context is therefore not forced into one rigid global filename convention.

Legacy capsules with useful `.context/` content are transitioned with `adopt`, not reinstall. Adoption preserves existing project files and enriches them with Core metadata/navigation.

## Additional semantic rules

Durable context uses typed semantics including FACT, DECISION, REQUIREMENT, RULE, PREFERENCE, HYPOTHESIS, BLOCKER, OPEN, and DEPRECATED.

Superseded decisions remain traceable. Recovery must reconcile the capsule with live facts from the authoritative branch and relevant CI/runtime evidence.
