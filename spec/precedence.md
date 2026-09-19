# Context precedence

When recovering a project, use the following precedence:

1. verified repository/runtime facts at the current authoritative branch/commit;
2. explicit active project rules indexed by `.context/manifest.json`;
3. accepted durable decisions;
4. current state;
5. latest handoff;
6. dialogue evidence when chronology/reasoning matters;
7. other historical records.

The capsule is durable memory, not a substitute for verifying live state. If stored context conflicts with newer verified repository facts, live facts win and the capsule must be updated.

A superseded decision remains part of project history. Mark it superseded/deprecated and link to its replacement instead of silently rewriting it.
