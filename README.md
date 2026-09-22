# Context Capsule Core

**Current stable patch: v1.3.1.** v1.3.0 remains historical; v1.3.1 establishes one immutable canonical Core commit for installation provenance.

Context Capsule is repository-local durable project memory for fresh-chat continuation.

## v1.3 permanent product

The normal product surface is intentionally small:

- clean installation into a repository without an existing capsule;
- repository-local semantic context;
- structural `VALID` and separate recovery `READY`;
- deterministic bounded `recover` output for a fresh chat;
- safe repository-relative paths;
- managed Context Capsule blocks inside shared `AI_CONTEXT.md` and `AGENTS.md`;
- preservation of project-owned manifest extensions;
- exact Core provenance through `core_commit`;
- one-commit GitHub publication from an expected parent;
- non-destructive repair of installed v1.3 capsules;
- permanent authoritative context branches with discovery-only default branches for feature-branch projects.

The temporary legacy adoption bridge has been retired after migrating the only three known legacy repositories. Legacy support is not part of the permanent CLI.

## CLI

```bash
python installer/capsulectl.py install --target /repo --repository owner/name --branch main --core-commit <sha>
python installer/capsulectl.py install --target /repo-context --repository owner/name --branch context --discovery-branch main --core-commit <sha>
python installer/capsulectl.py discovery --target /repo-main --authoritative-branch context --discovery-branch main
python installer/capsulectl.py repair --target /repo --repository owner/name --branch main --core-commit <sha>
python installer/capsulectl.py validate --target .
python installer/capsulectl.py ready --target .
python installer/capsulectl.py recover --target .
```

Local `install/repair` commands are development helpers. Canonical repository mutation follows `INSTALL_PROTOCOL.md` and is published to GitHub as one commit.

## Permanent context branch

Repositories that develop through disposable feature branches should keep durable Context Capsule authority on one permanent branch, for example context. The default branch remains a discovery-only gateway. Feature branches record their live-work identity inside semantic state; they do not become Context Capsule authority.
