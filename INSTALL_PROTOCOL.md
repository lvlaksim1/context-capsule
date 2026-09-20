# Context Capsule installation and transition protocol

## Permanent path: clean installation

Use `install` only when the target has no existing `.context/`.

1. Check out the branch that will be the authoritative context branch.
2. Start from a clean capsule/discovery working set.
3. Run:
   ```bash
   python installer/capsulectl.py install --target /repo --repository owner/name
   ```
4. Keep any pre-existing project instructions in `AGENTS.md` / `AI_CONTEXT.md`; Core adds only its managed block.
5. Replace every `CAPSULE_TODO` semantic template with repository-specific verified content.
6. Record durable rules/decisions and a concise handoff.
7. Reconcile those semantics with the live repository, CI/release evidence and any declared runtime authority.
8. Create an evidence-backed `checkpoint --ready`.
9. Run `audit --ready` and the repository-local runtime check.
10. Commit the capsule changes so the ready state is actually durable.

A fresh install is expected to be structurally valid immediately and **not ready** until steps 5-9 are completed.

## Branch topology

The checked-out branch is the authoritative branch for lifecycle mutation. Supplying `--branch` is a precondition check, not a request to switch branches.

For a split topology:

```bash
--branch work-context --discovery-branch main
```

The discovery branch must already exist. Lifecycle mutation is performed on the authoritative branch; do not create a second independent capsule on the discovery branch.

## Mutation safety

Before a mutating lifecycle command:

- commit/stash existing capsule/discovery changes, or deliberately use `--allow-dirty-context`;
- optionally supply `--expected-head <sha>`;
- do not use symlinked capsule paths.

Core computes the complete target state before writing. If preflight fails, no target file is written. During apply it uses a repository-local OS lock, compares the snapshot/HEAD/branch, journals preimages in Git metadata and rolls back a failed cooperating-writer transaction.

## Existing legacy capsule — temporary transition only

Until the three historical installations are migrated, use `adopt` when useful `.context/` exists but `.context/capsule.json` does not.

Adoption preserves:

- unknown legacy manifest fields;
- richer/nonnormalized project and current paths;
- declared decisions/dialogues/history outside standard folders;
- project-specific rule files;
- custom bootstrap text;
- split authoritative/discovery branches;
- `.agent/` or other declared volatile runtime authority.

Known historical Core bootstrap text may be replaced by the current managed block. Unknown text is preserved verbatim outside that block and recorded in `resume.bootstrap_review`; a ready checkpoint then requires explicit review.

`upgrade` follows the declared temporary migration chain. Current transition support is v1.0 -> v1.1 -> v1.2 -> v1.3.

After `fgis-fsa-il`, `telegram-receiver` and `ai-agent-lab` are migrated and verified, removal of the legacy/adoption migration layer should be handled as a separate change.

## Repair

`repair` is for a current-version installed capsule. It restores/refreshes Core-managed structure and navigation without overwriting project-owned semantic documents.

It does not silently bless recovered content as ready. Readiness is still governed by the semantic checkpoint.

## Prohibited

- reverse synchronization of project context into Core;
- telemetry or a central installation/context registry;
- silent migration of unknown historical content;
- flattening richer legacy semantics merely to fit standard filenames;
- copying routine runtime churn into durable context;
- treating structural validation as proof of semantic readiness.
