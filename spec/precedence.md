# Context precedence

When recovering a project, use the following order:

1. repository facts at the current commit;
2. explicit active project rules in `.context/rules/`;
3. accepted durable decisions in `.context/decisions/`;
4. current state in `.context/current/`;
5. latest handoff in `.context/handoffs/latest.md`;
6. historical records in `.context/history/` when needed.

If a handoff conflicts with newer repository facts, repository facts win and the capsule should be updated.

Deprecated decisions must remain traceable rather than being silently rewritten.
