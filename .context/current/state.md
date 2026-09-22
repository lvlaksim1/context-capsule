# Current state

## FACT — v1.3.1 remains stable production

Stable Context Capsule v1.3.1 remains released on `main` and existing v1.3.1 consumers remain unchanged.

## FACT — Master Plan item 1 is complete

The v2 development line on `v2-manager-runtime` now has a normative Core-managed Project Manager Contract.

The Contract explicitly covers:

- stable runtime-independent identity and one-project responsibility;
- owner-message semantics and explicit authorization;
- bounded authority;
- beliefs/goals/intentions/plans;
- commitment lifecycle;
- evidence provenance and confirm/supersede/conflict;
- risk-scoped reconciliation;
- durable-memory admission, retrieval, revalidation, revision, and consolidation;
- Reinstate → Reconcile → Plan → Execute → Verify → Reflect → Persist;
- self-modification boundary;
- external-expertise boundary;
- persistence/privacy boundary.

The Contract is installed at `.context/manager/CONTRACT.md`, referenced by the manifest, and is mandatory recovery state.

## FACT — deterministic verification is green

Current development Core provenance: `8b91e41737615f3c54ff87b193d8df6a6a886644`.

GitHub Actions run `35797459058` completed successfully:

- 26 permanent tests: PASS;
- lifecycle modules compile: PASS;
- self validation: VALID;
- self Project Manager readiness: READY;
- self reinstantiation smoke: PASS;
- isolated consumer compatibility smoke against `lvlaksim1/evrasia-hd-testbed`: PASS.

The consumer smoke cloned the testbed read-only into the CI runner, applied the current Core only to that temporary copy, then passed `repair → validate → ready → recover` while preserving `evrasia-hd-project-manager`. The GitHub testbed repository was not modified.

Two intermediate staged-integration commits produced failing CI while the Contract and validation changes were not yet coherent; the final coherent state fixed those compatibility failures and passed.

## FACT — next architectural stage is separate

The remaining major architecture questions are no longer foundational Project Manager gaps. They belong to Master Plan item 2: the Minimal Service Agent Base for future Supervisor, Auditor, Specialist Agents, and Agent Factory.

No stable v2 release or consumer migration has been authorized.
