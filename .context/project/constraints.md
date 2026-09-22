# Project constraints

## RULE — Architectural constraints

- No consumer project context, telemetry, installation registry, or central memory collection may flow into Core.
- Stable v1.3.1 consumers must not be silently upgraded to v2.
- Major upgrade is explicit and must preserve project-owned context.
- Universal manager behavior belongs to Core; project-specific authority belongs to the repository-local mandate.
- Manager beliefs must distinguish evidence/provenance from inference and untrusted content.
- Runtime conversation/checkpoint state is not durable manager identity.
- Repair must not perform a major-version upgrade.
- Secrets and hidden chain-of-thought are never durable manager memory.
