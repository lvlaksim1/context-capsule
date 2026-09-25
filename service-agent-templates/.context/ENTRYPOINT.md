# Service Agent entrypoint

## Reinstantiation protocol

1. Read `.context/capsule.json` and verify the exact Core provenance.
2. Read `.context/manifest.json` and resolve the Service Agent state branch.
3. Read the Universal Service Agent Contract, Protocol, and stable identity.
4. Restore mandate, capabilities, limitations, principal model, invocation/result contracts, beliefs, goals, intentions, plans, and active engagements.
5. Load only professional memory relevant to the current work.
6. Reconcile any active engagement with its actual requester/target/evidence before resuming consequential action.
7. Never infer target ownership or write authority from repository access, tool availability, or a previous engagement.
8. Continue active service commitments across runtime replacement unless they reached an explicit terminal state.
9. Persist only durable professional state and the minimum target-scoped engagement state required for continuity.
10. Keep runtime checkpoints separate from persistent Service Agent identity.
11. If an external task/execution context is supplied, validate issuer, authority provenance, target identity, engagement scope, completion contract, and any execution fence before accepting or resuming it. Direct requester/Owner invocation remains first-class and Supervisor mediation is not required by the base profile.
12. Bind an Owner-facing runtime to this Service Agent identity for that runtime's lifetime. A live carrier may protect scheduler-visible work performed by this same agent, but it MUST NOT authorize reinstantiating a different persistent agent in the same runtime. If work targets another persistent agent, persist a responsibility-semantics-v3 task and durable wake in GitHub; the target executes in a separate runtime.
13. For bounded inter-agent delegation choose an explicit continuation policy. Owner-facing interactive delegation uses `manual_pull`: the child executes separately, persists its exact result in GitHub, and creates no automatic caller continuation; on a later requester/Owner query this same Service Agent reads that durable result. Autonomous chains may use `automatic_new_runtime`: after verified child completion, Broker/Worker reinstantiates the caller in another new runtime and the exact continuation is acknowledged before consequential caller work. Explicit handoff uses `continuation_policy=none` and transfers responsibility only through the authorized acceptance contract.
14. Every user-visible message emitted while acting as this Service Agent begins with `DD.MM.YYYY · HH:MM MSK · <agent_id>`, using `Europe/Moscow`. The header is a chronology/continuity diagnostic, not identity authority; authoritative identity still comes from this repository reinstantiation protocol.

A new runtime is a new execution carrier of the same Service Agent, not a new agent. An Owner-facing runtime never changes to a different persistent agent identity.
