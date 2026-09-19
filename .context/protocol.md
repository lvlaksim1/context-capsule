# Context Capsule protocol

## Purpose

Preserve enough project meaning to continue work safely in a fresh chat or agent without reconstructing decisions from raw history.

## Navigation

`.context/manifest.json` is the navigation index. File names inside project-owned categories are not required to be globally identical; the manifest records the actual paths.

## Record semantics

- **FACT** — verified observation.
- **DECISION** — accepted architecture or implementation choice.
- **REQUIREMENT** — behavior that must hold.
- **RULE** — durable project operating rule.
- **PREFERENCE** — user preference affecting implementation.
- **HYPOTHESIS** — unverified explanation.
- **BLOCKER** — condition preventing progress.
- **OPEN** — unresolved work or question.
- **DEPRECATED** — old approach retained only for traceability.

## Update rules

- Record significant changes, not every conversational message.
- Preserve superseded decisions and explain their replacement.
- Keep secrets, tokens, and unnecessary personal data out of the capsule.
- Before handoff, update current state, manifest index, and `handoffs/latest.md`.
- Git/code/runtime evidence is authoritative for implementation facts; the capsule explains why the project is in that state and where work should resume.
- After restoring context, verify the live authoritative branch and relevant CI/runtime state before editing.
