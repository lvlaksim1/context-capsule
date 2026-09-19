# Project constraints

## RULE — Architectural constraints

- No target project context, telemetry, installation statistics, or central registry may flow into Core.
- Installed capsules must work without Core during normal project operation.
- Version changes are explicit and migration-driven.
- Adopt/repair/upgrade must not overwrite project-owned context.
- Legacy rich structures must be preserved where they carry more information than generic templates.
- Context mutation should use branch/HEAD-aware concurrency protection where available.
