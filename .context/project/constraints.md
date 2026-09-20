# Project constraints

## RULE — Architectural constraints

- No target project context, telemetry, installation statistics, or central registry may flow into Core.
- Installed capsules must work without Core during normal project operation.
- Version changes are explicit; no silent auto-upgrade.
- Repair must not overwrite project-owned context or silently change recorded branch topology.
- New clean installations are single-branch; existing explicit redirect topology remains supported installed state.
- Context mutation should use branch/HEAD-aware concurrency protection where available.
- Legacy repository-specific migration code is not part of the permanent product surface.
