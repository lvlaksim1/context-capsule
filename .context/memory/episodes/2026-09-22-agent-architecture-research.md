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

## Follow-up — authority locus

The first live cold-reinstantiation test revealed that product authority and persistent manager-state authority must be separate coordinates.

External practice reviewed for this correction:

- Letta MemFS projects agent memory into a git-backed memory repository; memory changes become future context after commit, and memory maintenance can occur in sibling git worktrees before merge.
- Letta also supports binding persistent memory to a custom memory repository, reinforcing that persistent agent context need not be identical to the product workspace.
- Microsoft Agent Framework rehydration requires stable logical agent/executor identities across reconstructed workflow instances and explicitly separates checkpoint/run state from the logical agent identity.

Manager synthesis: Context Capsule should not infer persistent-manager authority from whichever code branch happens to be executing. Durable manager state needs an explicit authority locus; product truth needs a separate baseline. This led to DEC-0012.
