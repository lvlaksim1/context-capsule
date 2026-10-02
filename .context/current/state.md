# Current state

Context Capsule v2 remains development-only on `v2-manager-runtime`; stable `main` and known consumers are unchanged.

Owner-directed Durable Finding Gate implementation is ACTIVE.

Scope:
- normative Project Manager Contract/Protocol;
- installed Project Manager templates and ENTRYPOINT;
- generated manifest policy + validation;
- deterministic regression coverage;
- no stable v1.3.1 promotion and no consumer migration.

The design criterion is explicit: a verified finding becomes mandatory durable state when it can materially change a reasonable future Manager's action or prevent repetition of a problem already solved. Runtime-only checkpoint/mailbox/trace/log/chat state is evidence, not durable managerial memory.
