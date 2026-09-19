# Context Capsule Core

Context Capsule is a repository-local project memory standard. This repository is the canonical Core implementation and contains installation, legacy adoption, validation, repair, upgrade, schemas, templates, and lifecycle rules.

It MUST NOT store, aggregate, or receive context from repositories into which a capsule is installed.

## Core model

- `capsule.json` is the technical passport: schema, installed Core version, source, target repository, update policy.
- `manifest.json` is the project navigation index: authoritative branch and actual paths to rules, state, handoff, decisions, dialogues, and history.
- Project-owned context stays entirely in the target repository.
- Installed capsules operate autonomously; Core is needed only for lifecycle operations.
- Versions are pinned and upgrades are explicit.
- Legacy capsules are **adopted**, not reinstalled.

## Commands

```bash
python installer/capsulectl.py install --target /path/to/repository --repository owner/name --branch main
python installer/capsulectl.py adopt --target /path/to/repository --repository owner/name --branch main
python installer/capsulectl.py validate --target /path/to/repository
python installer/capsulectl.py repair --target /path/to/repository --branch main
python installer/capsulectl.py upgrade --target /path/to/repository --branch main
```

See `spec/architecture.md`, `spec/lifecycle.md`, and `INSTALL_PROTOCOL.md`.
