# Project architecture

## DECISION — Architecture

Core contains templates, schemas, lifecycle tooling, migrations, tests, and specifications.

Each target repository contains its own installed `AI_CONTEXT.md`, `AGENTS.md`, `.context/`, and technical metadata. `capsule.json` identifies the Core installation/version. `manifest.json` maps the real context paths and branch topology.

Projects may have a separate volatile runtime authority such as `.agent/`; Context Capsule stores durable semantics and promotes only meaningful consequences from that runtime.
