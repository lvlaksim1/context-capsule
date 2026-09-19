# Context Capsule Core

Context Capsule is a repository-local project memory standard.

This repository is the canonical source for the capsule format, installer, validator, lifecycle rules, and migrations. It MUST NOT store, aggregate, or receive context from repositories into which a capsule is installed.

## Core model

- `context-capsule` is the central implementation and standard.
- Every target repository stores its complete project context locally in `AI_CONTEXT.md` and `.context/`.
- Installed capsules run autonomously. The central repository is required only for install, validate, upgrade, or repair operations.
- Project context never synchronizes back to this repository.
- Installed capsule versions are pinned. Upgrades are explicit and migration-driven.

## Operations

```bash
python installer/capsulectl.py install --target /path/to/repository --repository owner/name
python installer/capsulectl.py validate --target /path/to/repository
python installer/capsulectl.py repair --target /path/to/repository
python installer/capsulectl.py upgrade --target /path/to/repository
```

The installer only creates or repairs system-owned capsule files. Project-owned context is never exported to Context Capsule Core.

See `spec/architecture.md` and `spec/lifecycle.md`.
