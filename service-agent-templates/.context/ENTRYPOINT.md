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
12. Determine the current task/chain carrier before scheduler use. If a fresh live carrier exists, keep the durable handoff in GitHub and reinstate the next persistent agent directly in the same live runtime; do not let scheduler infrastructure advance that task. Do not globally disable scheduler infrastructure because the Owner is present: unrelated tasks without fresh live carriers remain independently eligible for autonomous execution.

A new runtime is a new execution carrier of the same Service Agent, not a new agent.
