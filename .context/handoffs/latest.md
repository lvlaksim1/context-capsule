# Latest handoff — implementation checkpoint, NOT a release

## Current user objective

Improve Context Capsule for seamless continuation in a fresh chat. See `DEC-0006-clean-install-and-temporary-legacy.md`. Keep temporary migration mechanisms until the three existing projects are migrated. The user requests concise stage reports and low token overhead.

## Source and scope

Baseline: upstream main `2965c17e5545e641ed7c0b4038a44885e3726a05`, Core v1.2.0. This checkpoint is on a separate development branch; main is intentionally unchanged. No target project has been migrated in this work.

## Completed

- Recorded the corrected product boundary and reporting requirement.
- Added initial, UNINTEGRATED implementation drafts:
  - `runtime/contracts.py`: repository path confinement, symlink rejection, validator for the bundled schema vocabulary, managed-block parsing.
  - `runtime/capsule_runtime.py`: read-only structural/readiness checks, context fingerprints and bounded task-specific recovery packs.
  - `installer/storage.py`: Git metadata lock, snapshot checks, atomic per-file replacement, rollback journal and interrupted-operation recovery.
  - `installer/legacy.py`: extracted legacy shape readers, preserving declared references and nested runtime extras.
  - `migrations/legacy-bootstrap-hashes.json`: hashes retrieved from actual historical templates, for recognizing system-owned old bootstrap text.

## IMPORTANT: incomplete integration

`installer/capsulectl.py` is STILL the original v1.2 implementation. An attempted replacement patch was rejected and made no changes. VERSION, existing schemas, templates and tests are also still v1.2. Do not report the audited defects as fixed.

The new runtime expects schema_version 3, managed_files metadata, `.context/resume.json`, `.context/index.json`, and installed local schemas/tools; NONE of that is wired yet. These modules are development drafts, not an available feature.

## Verification at checkpoint

All nine unchanged v1.2 lifecycle tests passed. Compilation of all four draft Python modules passed. This confirms baseline continuity and syntax only; new safety guarantees have not been tested.

## Next concrete stage

Integrate the smallest safe lifecycle change: use a staged mutation plan, strict preflight, branch/HEAD and dirty-context checks, then storage transaction apply. Preserve existing CLI commands; label migration paths temporary. Add focused negative tests before claiming guarantees. Avoid rewriting unrelated code.

Then connect bundled-schema validation, managed bootstrap upgrades and ready/draft recovery checkpoints. Add local recovery tooling only with schemas/templates and an offline end-to-end test. Update documentation and central capsule last.

## Known review items in drafts

- Validate journal input and permissions carefully; test rollback, interruption, stale lock, symlink and concurrent-edit behavior on Windows as well as Linux.
- Per-file atomic replace plus cooperative locks is not isolation against arbitrary non-cooperating writers. Do not claim otherwise.
- Readiness is structural/evidence-based, not proof that an LLM understands or obeys context.
- Preserve all unknown project fields and custom references during temporary legacy operations.
- Managed-block migration must preserve user instructions; unknown legacy bootstrap requires explicit reconciliation, never silent replacement.

## Audit findings to fix

Original v1.2 drops custom nested manifest fields and nonstandard indexed paths during repair; follows symlinks outside target; accepts invalid schema fields; labels upgrades successful without updating existing bootstrap; leaves partial writes after failure; does not enforce checkout branch; cannot protect dirty context using HEAD alone; may leave AGENTS disconnected; and reports empty context as valid.

## Publication discipline

Development branch: `work/seamless-context-v1.3`. Its manifest points to this branch so a fresh chat does not accidentally restore main. Return authority/discovery to main only when preparing the completed release.

Do not merge this unfinished checkpoint into main. Complete focused tests and end-to-end verification first. Save another short handoff at each significant stage.
