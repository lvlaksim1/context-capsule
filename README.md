# Context Capsule Core

Context Capsule is repository-local durable project memory for fresh-chat continuation.

## v1.3 development model

The permanent product is intentionally small:

- clean installation into a repository without an existing capsule;
- one repository-local semantic context;
- structural `VALID` and separate recovery `READY`;
- deterministic `recover` output for a fresh chat;
- safe repository-relative paths;
- managed Context Capsule blocks inside shared `AI_CONTEXT.md` and `AGENTS.md`;
- preservation of project-owned manifest extensions;
- exact Core provenance through `core_commit`;
- one-commit GitHub publication from an expected parent.

Legacy adoption is temporary and limited to the three known repositories named in `spec/v1.3.md`.

## CLI

```bash
python installer/capsulectl.py validate --target .
python installer/capsulectl.py ready --target .
python installer/capsulectl.py recover --target .
```

Local `install/adopt/repair` commands are development helpers. Canonical repository mutation follows `INSTALL_PROTOCOL.md` and is published to GitHub as one commit.
