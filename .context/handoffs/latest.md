# Latest handoff

Persistent manager:
- `manager_id = context-capsule-project-manager`
- repository: `lvlaksim1/context-capsule`
- manager-state branch: `v2-manager-runtime`
- product authority branch: `main`

Latest Owner clarification establishes **task-scoped interactive-first execution**, not global interactive scheduler shutdown.

Required semantics:
- GitHub is the durable handoff channel;
- when the Owner is online, the next agent for the current task/chain is reinstantiated immediately in the same live runtime;
- that task/chain carries a renewable live-carrier lease to prevent duplicate scheduler execution;
- Broker/Worker remain available for unrelated autonomous tasks;
- after live-carrier expiry, only that task may fall back autonomously when its policy permits;
- explicit holds are per-task.

Core implementation snapshot:
`bef230aa1599fd7ef04beabc19c6e42f5c1ec5e7`

Binding commit:
`90741e192a6ea49110f7edab4c463e329c89e736`

A test-assertion-only follow-up was committed after binding; hosted CI and fresh independent acceptance remain required.

Historical CCPM/ACP-CC findings remain CLOSED unless new evidence changes their mechanisms. Stable `main`, stable-v2 publication, and consumer migration remain unauthorized.
