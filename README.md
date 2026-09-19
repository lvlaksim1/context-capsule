# Context Capsule Core

Context Capsule is a repository-local durable project-memory standard. This repository is the canonical Core implementation; it never stores context from installed target repositories.

## v1.2 model

- `capsule.json` — technical installation/version passport.
- `manifest.json` — navigation, branch topology, runtime authority, sync policy.
- `project/` — stable identity, goals, architecture, constraints.
- `current/` — compact state, blockers, next actions.
- `decisions/`, `dialogues/`, `history/` — durable evidence/history layers.
- optional separate runtime authorities such as `.agent/` remain volatile; only semantic consequences are promoted into `.context/`.

## Lifecycle

```bash
python installer/capsulectl.py install --target /repo --repository owner/name --branch main
python installer/capsulectl.py adopt --target /repo --repository owner/name --branch main
python installer/capsulectl.py validate --target /repo
python installer/capsulectl.py audit --target /repo
python installer/capsulectl.py repair --target /repo --expected-head <sha>
python installer/capsulectl.py upgrade --target /repo --expected-head <sha>
```

For a context branch different from the discovery/default branch, pass `--branch <context-branch> --discovery-branch <default-branch>`.

See `spec/architecture.md`, `spec/lifecycle.md`, `spec/semantic-sync.md`, and `spec/branching.md`.
