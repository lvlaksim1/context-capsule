# Episode — Agent architecture research for Context Capsule v2

## Situation

The project direction changed from storing project experience to carrying a persistent Project Manager with experience across replaceable runtimes.

## Findings retained

- Letta MemFS demonstrates a Git-backed context repository with always-loaded system memory plus deeper on-demand memory.
- LangGraph distinguishes runtime/thread checkpoint state from long-term store memory.
- AutoGen and other agent frameworks separate agent/component definition from serializable runtime state, reinforcing runtime-independent identity.
- BDI architecture provides a useful separation of beliefs, goals, intentions, and plans.
- Microsoft Agent Framework's harness concept reinforces that operational discipline (planning, todo/state handling, approvals, compaction) is distinct from model personality.
- OpenAI manager-style orchestration supports a central accountable manager using specialists as subordinate tools/experts rather than peers with equal authority.
- OWASP and related work highlight persistent-memory poisoning, making provenance/authority a first-class memory property.

## Consequence

v2 uses a universal Manager Protocol, stable manager identity, BDI-style active state, typed memory, explicit belief provenance, a runtime-checkpoint boundary, and explicit major-version upgrade.
