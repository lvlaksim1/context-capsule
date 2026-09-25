# Service Agent Runtime Identity

This file is the authoritative runtime-routing supplement for Service Agents and supersedes older same-runtime handoff/return wording in the universal Service Agent Protocol.

- An Owner-facing runtime remains bound to one persistent `agent_id`.
- A different target `agent_id` always executes in a separate runtime.
- Keep authority/responsibility semantics version 2.
- Delegated target tasks carry `runtime:separate-target`.
- Owner-facing delegation adds `continuation:manual-pull`: the child result remains durable in GitHub until the Owner asks the caller to inspect it.
- Autonomous delegation adds `continuation:automatic-new-runtime`: the caller precreates a dependency-bound continuation task carrying `runtime:caller-continuation`; the scheduler later reinstantiates the caller in a new runtime.
- Same-runtime persistent identity switching is forbidden.
- Every user-visible Service Agent message starts with `DD.MM.YYYY · HH:MM MSK · <agent_id>` using `Europe/Moscow`.
- The visible header is diagnostic only; repository reinstantiation remains identity authority.
