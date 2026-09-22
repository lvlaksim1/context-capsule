# Manager plans

## Completed — Master Plan item 2

1. Derive only the properties genuinely shared by external persistent service roles.
2. Define the Universal Service Agent Contract and Protocol.
3. Implement a separate Service Agent profile with stable `agent_id`, role/specialization, mandate, capabilities, limitations, principal model, invocation/result contracts, BDI state, active engagements, and professional memory.
4. Enforce target ownership isolation, explicit engagement authority, advisory-by-default behavior, non-escalating transport authority, and no self-expansion.
5. Add machine-readable identity, manifest, invocation, and result schemas.
6. Add `service-install`, `service-repair`, `service-validate`, `service-ready`, and `service-recover`.
7. Verify with 36 permanent tests and a full Service Agent CLI lifecycle smoke.

## Current plan

1. Begin Master Plan item 3: create the first real Service Agent profile, Supervisor, in its own repository.
2. Seed Supervisor from the temporary Supervisor context already created with the owner, but transform it into structured Service Agent state rather than treating the seed Markdown as authoritative by itself.
3. Give Supervisor portfolio-level memory and coordination authority without copying full project-local context or granting unrestricted project write authority.
4. Verify Supervisor reinstantiation independently before using it to help create the Auditor.
5. Keep stable v1.3.1 and existing consumers unchanged.
