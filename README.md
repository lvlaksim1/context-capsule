# Context Capsule Core

Context Capsule is a repository-local durable project-context standard for continuity across independent human/AI sessions. The target repository owns its complete context; Core supplies the format, installer and verification tooling and never receives project memory back.

## v1.3 model

Every installed capsule has two distinct states:

- **structurally valid** — files, schemas, references and managed runtime are internally consistent;
- **continuation-ready** — project-specific semantics have been filled, reconciled with live evidence, indexed, fingerprinted and recorded in an evidence-backed checkpoint.

Core files:

- `.context/capsule.json` — pinned Core version plus integrity hashes for Core-managed bootstrap/runtime files;
- `.context/manifest.json` — semantic navigation, branch topology, runtime authority and sync policy;
- `.context/project/` — stable identity, goals, architecture and constraints;
- `.context/current/` — compact current state, blockers and next actions;
- `.context/decisions/`, `dialogues/`, `history/` — durable evidence/history;
- `.context/index.json` — small semantic routing index for selective recall;
- `.context/resume.json` — evidence-backed continuation checkpoint;
- `.context/tools/` — repository-local offline validator/recovery runtime and bundled schemas.

Optional fast-changing authorities such as `.agent/` remain separate. Only their durable semantic consequences belong in Context Capsule.

## Clean installation

Clean installation is the permanent product path:

```bash
python installer/capsulectl.py install \
  --target /repo \
  --repository owner/name
```

The installer refuses an existing `.context/`, preserves pre-existing `AGENTS.md` / `AI_CONTEXT.md` text, adds a Core-managed discovery block and creates a **draft** checkpoint. The project-specific `CAPSULE_TODO` documents must then be filled from verified repository evidence.

After reconciliation:

```bash
python installer/capsulectl.py checkpoint \
  --target /repo \
  --summary "Verified current position" \
  --next-action "Next concrete action" \
  --evidence-file path/to/evidence \
  --ready
```

A ready checkpoint is not a claim that an LLM will understand or obey the project. It is an evidence-backed statement that the repository contains the required continuation material and that the working set has not semantically changed since the checkpoint.

## Validation and recovery

```bash
python installer/capsulectl.py validate --target /repo
python installer/capsulectl.py audit --target /repo --ready
python .context/tools/capsule_runtime.py check --ready
python .context/tools/capsule_runtime.py resume --task "current task"
```

`resume` builds a bounded recovery pack: mandatory project/current/rule/handoff context plus a small number of task-relevant indexed records. It fails rather than silently dropping required constraints when the configured byte budget is exceeded.

## Safe lifecycle mutation

Mutating commands operate as:

`preflight -> complete mutation plan -> repository lock -> snapshot recheck -> journal -> atomic per-file replace -> commit journal state / rollback`.

They also enforce repository path confinement, reject symlink/special-file escape, verify the checked-out authoritative branch, guard HEAD when requested and refuse dirty capsule/discovery files unless explicitly allowed.

The lock protects cooperating Context Capsule writers. It is not global isolation from arbitrary external processes; snapshot/file checks detect relevant concurrent edits before overwrite.

## Temporary legacy transition

`adopt` and chained legacy `upgrade` support are intentionally temporary. They exist only to migrate and verify the pre-Core capsules currently installed in:

- `lvlaksim1/fgis-fsa-il`;
- `lvlaksim1/telegram-receiver`;
- `lvlaksim1/ai-agent-lab`.

They preserve richer legacy layouts, custom manifest fields, custom bootstrap instructions, branch redirects and separate runtime authority. Unknown bootstrap text is preserved and blocks a ready checkpoint until explicitly reviewed.

Do not remove these mechanisms until all three real migrations are complete and verified. Their later removal is a separate evidence-gated change.

See `INSTALL_PROTOCOL.md` and `spec/`.
